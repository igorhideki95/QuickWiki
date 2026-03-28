from __future__ import annotations

import asyncio
import html
import hashlib
import logging
import random
from datetime import UTC, datetime
from typing import Any
from urllib import robotparser
from urllib.parse import quote, unquote, urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown

from .config import ScraperConfig
from .extractor import PageExtractor
from .models import PageDocument
from .reporting import build_runtime_status
from .site_profiles import resolve_site_profile
from .storage import StorageManager
from .url_utils import canonicalize_url, infer_asset_bucket, make_absolute_url


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class AsyncRateLimiter:
    def __init__(self, rate_per_second: float) -> None:
        self.rate_per_second = max(0.0, float(rate_per_second))
        self._lock = asyncio.Lock()
        self._next_time = 0.0

    async def wait(self) -> None:
        if self.rate_per_second <= 0:
            return
        interval = 1.0 / self.rate_per_second
        loop = asyncio.get_running_loop()
        async with self._lock:
            now = loop.time()
            if now < self._next_time:
                await asyncio.sleep(self._next_time - now)
                now = loop.time()
            self._next_time = max(now, self._next_time) + interval


class QuickWikiCrawler:
    def __init__(self, config: ScraperConfig) -> None:
        self.config = config
        self.logger = logging.getLogger("quickwiki.scraper")
        self.profile = resolve_site_profile(
            self.config.site_profile,
            self.config.seed_url,
            profiles_dir=self.config.profiles_dir,
            extra_profile_files=self.config.site_profile_files,
        )

        self.storage = StorageManager(self.config.normalized_output_dir())
        self.extractor = PageExtractor(self.profile)
        self.rate_limiter = AsyncRateLimiter(self.config.rate_limit_per_sec)
        self.run_config = self.config.to_runtime_dict()

        self.queue: asyncio.Queue[str | None] = asyncio.Queue()
        self.state_lock = asyncio.Lock()
        self.visited: set[str] = set()
        self.enqueued: set[str] = set()
        self.failed_pages: dict[str, str] = {}
        self.asset_download_semaphore = asyncio.Semaphore(max(1, self.config.asset_workers_per_page))
        self.asset_task_lock = asyncio.Lock()
        self.asset_download_tasks: dict[str, asyncio.Task[dict[str, Any] | None]] = {}
        self.robot_rules: robotparser.RobotFileParser | None = None
        self.enqueue_soft_cap: int | None = (
            None
            if self.config.max_pages is None
            else max(self.config.max_pages * 3, self.config.max_pages + (self.config.workers * 3))
        )

        self.stats: dict[str, Any] = {
            "started_at": datetime.now(UTC).isoformat(),
            "site_profile": self.profile.key,
            "site_label": self.profile.label,
            "pages_attempted": 0,
            "pages_saved": 0,
            "pages_failed": 0,
            "links_discovered": 0,
            "assets_downloaded": 0,
            "assets_reused": 0,
            "assets_failed": 0,
            "skipped_robots": 0,
            "http_pages_saved": 0,
            "api_pages_saved": 0,
            "api_seed_urls_discovered": 0,
            "retry_rounds_completed": 0,
            "pages_retried": 0,
            "failed_pages_recovered": 0,
            "source_pages_captured": 0,
        }
        self.current_phase = "starting"
        self._persist_runtime_status_now("starting")

    async def run(self) -> dict[str, Any]:
        pending = self._bootstrap_state()
        if not pending:
            self.logger.warning("Nenhuma URL pendente para processar.")
            self._finalize_stats()
            self.storage.finalize(
                self.stats,
                failed_pages=self.failed_pages,
                site_profile=self.profile,
                run_config=self.run_config,
            )
            self._persist_runtime_status_now("completed")
            return self.stats

        for url in pending:
            await self.queue.put(url)

        timeout = httpx.Timeout(self.config.timeout_seconds)
        limits = httpx.Limits(max_connections=max(self.config.workers * 2, 10), max_keepalive_connections=20)

        async with httpx.AsyncClient(
            headers={"User-Agent": self.config.user_agent},
            follow_redirects=True,
            timeout=timeout,
            limits=limits,
        ) as client:
            await self._persist_runtime_status("bootstrapping")
            await self._load_robots(client)
            await self._bootstrap_from_mediawiki_api(client)
            await self._persist_runtime_status("crawling")

            workers = [asyncio.create_task(self._worker_loop(client, idx)) for idx in range(self.config.workers)]
            await self.queue.join()
            for retry_round in range(1, self.config.retry_failed_passes + 1):
                requeued = await self._requeue_failed_pages_for_retry(retry_round)
                if not requeued:
                    break
                await self._persist_runtime_status("retrying")
                await self.queue.join()
                await self._persist_runtime_status("crawling")

            for _ in workers:
                await self.queue.put(None)
            await asyncio.gather(*workers, return_exceptions=False)

        self._finalize_stats()
        await self._persist_runtime_status("finalizing")
        self.storage.finalize(
            self.stats,
            failed_pages=self.failed_pages,
            site_profile=self.profile,
            run_config=self.run_config,
        )
        self.storage.save_checkpoint(
            visited=self.visited,
            pending=self.enqueued.difference(self.visited),
            stats=self.stats,
            failed_pages=self.failed_pages,
        )
        self._persist_runtime_status_now("completed")
        self.logger.info(
            "Execução concluída: %s páginas salvas, %s assets únicos.",
            self.stats["pages_saved"],
            len(self.storage.assets_by_hash),
        )
        return self.stats

    async def _worker_loop(self, client: httpx.AsyncClient, worker_id: int) -> None:
        while True:
            url = await self.queue.get()
            if url is None:
                self.queue.task_done()
                return

            try:
                await self._process_url(client, url, worker_id)
            except Exception:
                self.logger.exception("Falha inesperada ao processar %s", url)
                async with self.state_lock:
                    self.stats["pages_failed"] += 1
                    self.failed_pages[url] = "unexpected_exception"
                await self._persist_runtime_status()
            finally:
                self.queue.task_done()

    async def _process_url(self, client: httpx.AsyncClient, url: str, worker_id: int) -> None:
        async with self.state_lock:
            if url in self.visited:
                return
            if self.config.max_pages is not None and self.stats["pages_attempted"] >= self.config.max_pages:
                return
            self.visited.add(url)
            self.stats["pages_attempted"] += 1

        if self.robot_rules and not self.robot_rules.can_fetch(self.config.user_agent, url):
            self.logger.debug("Robots.txt bloqueou: %s", url)
            async with self.state_lock:
                self.stats["skipped_robots"] += 1
            await self._persist_runtime_status()
            return

        page_payload, failure_reason = await self._fetch_page_content(client, url)
        if page_payload is None:
            async with self.state_lock:
                self.stats["pages_failed"] += 1
                self.failed_pages[url] = failure_reason or "fetch_failed"
            await self._persist_runtime_status()
            return

        canonical_final = canonicalize_url(
            page_payload["final_url"],
            url,
            allowed_domains=self.profile.allowed_domains,
            allowed_prefix=self.profile.allowed_path_prefix,
        )
        if canonical_final and canonical_final != url:
            async with self.state_lock:
                self.visited.add(canonical_final)
                self.enqueued.add(canonical_final)
                self.failed_pages.pop(canonical_final, None)
            url = canonical_final
        elif canonical_final:
            url = canonical_final

        slug = self.storage.register_url(url)
        page = self.extractor.extract_page(
            url=url,
            slug=slug,
            html=page_payload["html"],
            source_encoding=page_payload.get("encoding"),
            internal_link_resolver=lambda to_slug: self.storage.html_relative_link(slug, to_slug),
            fetch_source=str(page_payload.get("source", "direct_http")),
        )
        page.site_profile = self.profile.key
        if self.config.capture_wiki_source:
            source_capture = await self._fetch_page_source(client, page_payload, url)
            if source_capture:
                page.wikitext = source_capture["wikitext"]
                page.source_edit_url = source_capture["source_edit_url"]
                page.source_raw_url = source_capture["source_raw_url"]
                page.source_templates = source_capture["source_templates"]
        if page_payload.get("api_links"):
            page.internal_links = sorted(set(page.internal_links).union(page_payload["api_links"]))
        if page_payload.get("api_categories"):
            page.categories = sorted(set(page.categories).union(page_payload["api_categories"]))
        if page_payload.get("api_templates"):
            seen = {
                (
                    "|".join(sorted(template.get("classes", []))),
                    template.get("preview", ""),
                )
                for template in page.templates
                if isinstance(template, dict)
            }
            for template_name in page_payload["api_templates"]:
                candidate = {"classes": ["api-template"], "preview": str(template_name)}
                key = ("api-template", str(template_name))
                if key in seen:
                    continue
                page.templates.append(candidate)
                seen.add(key)

        await self._download_and_rewrite_assets(client, page)
        self.storage.save_page(page)

        async with self.state_lock:
            had_failure_before = url in self.failed_pages
            self.stats["pages_saved"] += 1
            if page.fetch_source == "mediawiki_api":
                self.stats["api_pages_saved"] += 1
            else:
                self.stats["http_pages_saved"] += 1
            if page.wikitext:
                self.stats["source_pages_captured"] += 1
            self.failed_pages.pop(url, None)
            pages_saved = self.stats["pages_saved"]

        discovered = await self._enqueue_new_urls(page.internal_links)
        async with self.state_lock:
            self.stats["links_discovered"] += discovered
            if had_failure_before:
                self.stats["failed_pages_recovered"] += 1

        self.logger.info(
            "[worker=%s] Capturado %s | links=%s | imagens=%s",
            worker_id,
            url,
            len(page.internal_links),
            len(page.images),
        )

        if pages_saved % self.config.checkpoint_every_pages == 0:
            self.storage.save_checkpoint(
                visited=self.visited,
                pending=self.enqueued.difference(self.visited),
                stats=self.stats,
                failed_pages=self.failed_pages,
            )
        await self._persist_runtime_status()

    async def _fetch_page_content(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> tuple[dict[str, Any] | None, str | None]:
        response = await self._fetch_page_http(client, url)
        if response is not None and response.status_code < 400:
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                return (
                    {
                        "html": response.text,
                        "encoding": response.encoding,
                        "final_url": str(response.url),
                        "title": self._title_from_canonical_url(str(response.url)),
                        "source": "direct_http",
                    },
                    None,
                )
            self.logger.debug("Resposta não-HTML para %s (%s)", url, content_type)

        if response is not None and response.status_code == 403 and "just a moment" in response.text.lower():
            self.logger.debug("Cloudflare challenge em %s; tentando fallback MediaWiki API.", url)
        elif response is not None and response.status_code >= 400:
            self.logger.debug("HTTP %s em %s; tentando fallback MediaWiki API.", response.status_code, url)

        fallback = await self._fetch_page_via_api(client, url)
        if fallback is not None:
            return fallback, None

        if response is not None and response.status_code >= 400:
            self.logger.warning("HTTP %s em %s", response.status_code, url)
            return None, f"http_{response.status_code}"
        if response is not None:
            content_type = response.headers.get("content-type", "").lower() or "unknown"
            return None, f"non_html:{content_type}"
        return None, "transport_error_or_timeout"

    async def _fetch_page_http(self, client: httpx.AsyncClient, url: str) -> httpx.Response | None:
        for attempt in range(self.config.max_retries + 1):
            try:
                await self.rate_limiter.wait()
                response = await client.get(url)
                if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.config.max_retries:
                    delay = self.config.backoff_base_seconds * (2**attempt) + random.uniform(0.0, 0.35)
                    await asyncio.sleep(delay)
                    continue
                return response
            except httpx.TransportError as exc:
                if attempt >= self.config.max_retries:
                    self.logger.warning("Erro final em %s: %s", url, exc)
                    return None
                delay = self.config.backoff_base_seconds * (2**attempt) + random.uniform(0.0, 0.35)
                await asyncio.sleep(delay)
        return None

    async def _fetch_page_via_api(self, client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
        title = self._title_from_canonical_url(url)
        if not title:
            return None

        api_url = self._mediawiki_api_url()
        params = {
            "action": "parse",
            "page": title,
            "prop": "text|links|images|categories|templates",
            "format": "json",
            "redirects": "1",
        }
        response = await self._fetch_with_retry(client, api_url, expect_html=False, params=params)
        if response is None:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        parse_payload = payload.get("parse")
        if not isinstance(parse_payload, dict):
            return None

        text_payload = parse_payload.get("text")
        if not isinstance(text_payload, dict):
            return None
        html_fragment = text_payload.get("*")
        if not isinstance(html_fragment, str) or not html_fragment.strip():
            return None

        api_links: list[str] = []
        for link in parse_payload.get("links", []):
            if not isinstance(link, dict):
                continue
            link_title = link.get("*")
            if not isinstance(link_title, str) or not link_title.strip():
                continue
            canonical = canonicalize_url(
                f"/wiki/{link_title.strip().replace(' ', '_')}",
                url,
                allowed_domains=self.profile.allowed_domains,
                allowed_prefix=self.profile.allowed_path_prefix,
            )
            if canonical:
                api_links.append(canonical)

        api_categories = []
        for category in parse_payload.get("categories", []):
            if not isinstance(category, dict):
                continue
            cat_label = category.get("*")
            if isinstance(cat_label, str) and cat_label.strip():
                api_categories.append(cat_label.strip())

        api_templates = []
        for template in parse_payload.get("templates", []):
            if not isinstance(template, dict):
                continue
            template_name = template.get("*")
            if isinstance(template_name, str) and template_name.strip():
                api_templates.append(template_name.strip())

        title_text = parse_payload.get("title", title)
        title_text = title_text if isinstance(title_text, str) else title
        categories_html = "".join(
            f"<li><a href=\"/wiki/Categoria:{html.escape(label).replace(' ', '_')}\">{html.escape(label)}</a></li>"
            for label in api_categories
        )
        category_block = (
            f"<div id=\"mw-normal-catlinks\"><ul>{categories_html}</ul></div>" if categories_html else ""
        )
        wrapped_html = (
            "<html><body>"
            f"<h1 id=\"firstHeading\">{html.escape(title_text)}</h1>"
            f"<div id=\"mw-content-text\"><div class=\"mw-parser-output\">{html_fragment}</div>{category_block}</div>"
            "</body></html>"
        )

        final_url = canonicalize_url(
            f"/wiki/{title_text.replace(' ', '_')}",
            url,
            allowed_domains=self.profile.allowed_domains,
            allowed_prefix=self.profile.allowed_path_prefix,
        )
        return {
            "html": wrapped_html,
            "encoding": "utf-8",
            "final_url": final_url or url,
            "title": title_text,
            "source": "mediawiki_api",
            "api_links": sorted(set(api_links)),
            "api_categories": sorted(set(api_categories)),
            "api_templates": sorted(set(api_templates)),
        }

    async def _fetch_page_source(
        self,
        client: httpx.AsyncClient,
        page_payload: dict[str, Any],
        url: str,
    ) -> dict[str, Any] | None:
        title = str(page_payload.get("title") or self._title_from_canonical_url(page_payload.get("final_url", url)) or "")
        if not title:
            return None

        response = await self._fetch_with_retry(
            client,
            self._mediawiki_api_url(),
            expect_html=False,
            params={
                "action": "query",
                "prop": "revisions",
                "titles": title,
                "rvslots": "main",
                "rvprop": "content",
                "redirects": "1",
                "format": "json",
                "formatversion": "2",
            },
        )
        if response is None:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        query = payload.get("query")
        if not isinstance(query, dict):
            return None
        pages = query.get("pages")
        if not isinstance(pages, list) or not pages:
            return None
        page_info = pages[0]
        if not isinstance(page_info, dict) or page_info.get("missing"):
            return None

        resolved_title = str(page_info.get("title") or title).strip()
        revisions = page_info.get("revisions")
        if not isinstance(revisions, list) or not revisions:
            return None
        revision = revisions[0]
        if not isinstance(revision, dict):
            return None

        wikitext = ""
        if isinstance(revision.get("slots"), dict):
            main_slot = revision["slots"].get("main")
            if isinstance(main_slot, dict):
                wikitext = str(main_slot.get("content") or "")
        if not wikitext and isinstance(revision.get("content"), str):
            wikitext = revision["content"]
        wikitext = wikitext.strip()
        if not wikitext:
            return None

        normalized_title = resolved_title.replace(" ", "_")
        source_edit_url, source_raw_url = self.profile.build_source_urls(resolved_title)
        return {
            "title": resolved_title,
            "wikitext": wikitext,
            "source_edit_url": source_edit_url,
            "source_raw_url": source_raw_url,
            "source_templates": _extract_template_names_from_wikitext(wikitext),
        }

    async def _bootstrap_from_mediawiki_api(self, client: httpx.AsyncClient) -> None:
        if not self.config.should_bootstrap_from_api():
            return

        self.logger.info("Bootstrap de cobertura via MediaWiki API habilitado.")
        namespace_ids = await self._discover_namespace_ids(client)
        if not namespace_ids:
            self.logger.warning("Não foi possível descobrir namespaces pela API; seguindo apenas com BFS.")
            return

        api_url = self._mediawiki_api_url()
        total_discovered = 0

        for namespace_id in namespace_ids:
            params = {
                "action": "query",
                "list": "allpages",
                "aplimit": "max",
                "apnamespace": str(namespace_id),
                "format": "json",
            }
            namespace_discovered = 0

            while True:
                response = await self._fetch_with_retry(client, api_url, expect_html=False, params=params)
                if response is None:
                    break
                try:
                    payload = response.json()
                except ValueError:
                    break

                query = payload.get("query", {})
                pages = query.get("allpages", []) if isinstance(query, dict) else []
                candidates: list[str] = []
                for page in pages:
                    if not isinstance(page, dict):
                        continue
                    title = page.get("title")
                    if not isinstance(title, str) or not title.strip():
                        continue
                    canonical = canonicalize_url(
                        f"/wiki/{title.strip().replace(' ', '_')}",
                        self.config.seed_url,
                        allowed_domains=self.profile.allowed_domains,
                        allowed_prefix=self.profile.allowed_path_prefix,
                    )
                    if canonical:
                        candidates.append(canonical)

                discovered_now = await self._enqueue_new_urls(candidates)
                namespace_discovered += discovered_now
                total_discovered += discovered_now

                continuation = payload.get("continue")
                if not isinstance(continuation, dict):
                    break
                next_token = continuation.get("apcontinue")
                if not isinstance(next_token, str) or not next_token:
                    break
                params["apcontinue"] = next_token

            if namespace_discovered:
                self.logger.info(
                    "Namespace %s adicionou %s páginas ao frontier.",
                    namespace_id,
                    namespace_discovered,
                )

        async with self.state_lock:
            self.stats["api_seed_urls_discovered"] += total_discovered

        if total_discovered:
            self.logger.info("Bootstrap API concluiu com %s páginas extras descobertas.", total_discovered)
        else:
            self.logger.info("Bootstrap API não encontrou novas páginas além do frontier atual.")

    async def _discover_namespace_ids(self, client: httpx.AsyncClient) -> list[int]:
        response = await self._fetch_with_retry(
            client,
            self._mediawiki_api_url(),
            expect_html=False,
            params={
                "action": "query",
                "meta": "siteinfo",
                "siprop": "namespaces",
                "format": "json",
            },
        )
        if response is None:
            return []

        try:
            payload = response.json()
        except ValueError:
            return []

        query = payload.get("query")
        if not isinstance(query, dict):
            return []
        namespaces = query.get("namespaces")
        if not isinstance(namespaces, dict):
            return []

        namespace_ids: list[int] = []
        for raw_id in namespaces.keys():
            try:
                namespace_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            if namespace_id >= 0:
                namespace_ids.append(namespace_id)
        return sorted(set(namespace_ids))

    async def _download_and_rewrite_assets(self, client: httpx.AsyncClient, page: PageDocument) -> None:
        if not page.images:
            return

        remote_to_relative: dict[str, str] = {}
        tasks = [asyncio.create_task(self._process_page_image_asset(client, page, image)) for image in page.images]
        for result in await asyncio.gather(*tasks):
            if not result:
                continue
            remote_to_relative.update(result)

        if remote_to_relative:
            self._rewrite_asset_links(page, remote_to_relative)

    async def _process_page_image_asset(
        self,
        client: httpx.AsyncClient,
        page: PageDocument,
        image: Any,
    ) -> dict[str, str]:
        async with self.asset_download_semaphore:
            cached = self.storage.resolve_asset_by_url(image.original_url) or self.storage.resolve_asset_by_url(
                image.thumbnail_url
            )
            if cached:
                image.sha256 = cached["sha256"]
                image.bucket = cached["bucket"]
                image.local_asset_path = cached["relative_path"]
                async with self.state_lock:
                    self.stats["assets_reused"] += 1
                return {
                    image.original_url: cached["relative_path"],
                    image.thumbnail_url: cached["relative_path"],
                }

            bucket = infer_asset_bucket(
                page_url=page.url,
                image_url=image.original_url,
                alt=image.alt,
                title=image.title,
                context=image.context_text,
            )
            payload = await self._get_or_download_asset_bytes(client, image.original_url)
            if payload is None:
                payload = await self._get_or_download_asset_bytes(client, image.thumbnail_url)

            if payload is None:
                async with self.state_lock:
                    self.stats["assets_failed"] += 1
                return {}

            stored = self.storage.persist_asset(
                source_url=payload["url"],
                content=payload["content"],
                bucket=bucket,
                content_type=payload["content_type"],
            )
            self.storage.alias_asset_url(image.original_url, stored["sha256"])
            self.storage.alias_asset_url(image.thumbnail_url, stored["sha256"])

            image.sha256 = stored["sha256"]
            image.bucket = stored["bucket"]
            image.local_asset_path = stored["relative_path"]

            async with self.state_lock:
                self.stats["assets_downloaded"] += 1

            return {
                image.original_url: stored["relative_path"],
                image.thumbnail_url: stored["relative_path"],
            }

    async def _get_or_download_asset_bytes(self, client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
        async with self.asset_task_lock:
            task = self.asset_download_tasks.get(url)
            if task is None:
                task = asyncio.create_task(self._download_asset_bytes(client, url))
                self.asset_download_tasks[url] = task

        try:
            return await task
        finally:
            if task.done():
                async with self.asset_task_lock:
                    existing = self.asset_download_tasks.get(url)
                    if existing is task:
                        self.asset_download_tasks.pop(url, None)

    def _rewrite_asset_links(self, page: PageDocument, remote_to_relative: dict[str, str]) -> None:
        soup = BeautifulSoup(page.html_clean, "lxml")
        changed = False

        for image in soup.select("img"):
            candidates = []
            original_hint = make_absolute_url(image.get("data-original-src"), page.url)
            src_value = make_absolute_url(image.get("src"), page.url)
            if original_hint:
                candidates.append(original_hint)
            if src_value:
                candidates.append(src_value)

            for remote in candidates:
                relative = remote_to_relative.get(remote)
                if not relative:
                    continue
                image["src"] = self.storage.asset_relative_link_from_page(page.slug, relative)
                changed = True
                break

        if not changed:
            return

        page.html_clean = _serialize_html_fragment(soup)
        page.markdown = html_to_markdown(
            page.html_clean,
            heading_style="ATX",
            bullets="-",
            strip=["script", "style", "noscript", "iframe"],
        )
        page.content_hash = hashlib.sha256(page.markdown.encode("utf-8")).hexdigest()

    async def _download_asset_bytes(self, client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
        response = await self._fetch_with_retry(client, url, expect_html=False)
        if response is None:
            return None
        return {
            "url": str(response.url),
            "content_type": response.headers.get("content-type", ""),
            "content": response.content,
        }

    async def _fetch_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        expect_html: bool,
        params: dict[str, str] | None = None,
    ) -> httpx.Response | None:
        for attempt in range(self.config.max_retries + 1):
            try:
                await self.rate_limiter.wait()
                response = await client.get(url, params=params)
                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise httpx.HTTPStatusError(
                        f"retryable status {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                if response.status_code >= 400:
                    self.logger.warning("HTTP %s em %s", response.status_code, url)
                    return None

                content_type = response.headers.get("content-type", "").lower()
                if expect_html and "text/html" not in content_type:
                    self.logger.debug("Ignorando não-HTML em %s (%s)", url, content_type)
                    return None

                return response
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                if attempt >= self.config.max_retries:
                    self.logger.warning("Erro final em %s: %s", url, exc)
                    return None
                delay = self.config.backoff_base_seconds * (2**attempt) + random.uniform(0.0, 0.35)
                await asyncio.sleep(delay)
        return None

    def _title_from_canonical_url(self, url: str) -> str:
        canonical = canonicalize_url(
            url,
            url,
            allowed_domains=self.profile.allowed_domains,
            allowed_prefix=self.profile.allowed_path_prefix,
        )
        if not canonical:
            return ""
        parsed = urlparse(canonical)
        decoded_path = unquote(parsed.path)
        marker = self.profile.allowed_path_prefix.rstrip("/") + "/"
        if not decoded_path.startswith(marker):
            return ""
        return decoded_path[len(marker) :].replace("_", " ").strip()

    async def _enqueue_new_urls(self, urls: list[str]) -> int:
        discovered = 0
        async with self.state_lock:
            for url in urls:
                if url in self.visited or url in self.enqueued:
                    continue
                if self.enqueue_soft_cap is not None:
                    pending_count = len(self.enqueued.difference(self.visited))
                    if pending_count >= self.enqueue_soft_cap:
                        break
                self.enqueued.add(url)
                await self.queue.put(url)
                discovered += 1
        return discovered

    async def _requeue_failed_pages_for_retry(self, retry_round: int) -> int:
        if self.config.max_pages is not None:
            return 0

        async with self.state_lock:
            failed_urls = sorted(self.failed_pages)
            if not failed_urls:
                return 0
            for url in failed_urls:
                self.visited.discard(url)
                self.enqueued.add(url)
                await self.queue.put(url)
            self.stats["pages_retried"] += len(failed_urls)
            self.stats["retry_rounds_completed"] = retry_round

        self.logger.info(
            "Retry round %s: reenfileirando %s páginas que falharam.",
            retry_round,
            len(failed_urls),
        )
        return len(failed_urls)

    def _mediawiki_api_url(self) -> str:
        return self.profile.api_url()

    def _bootstrap_state(self) -> list[str]:
        seed = canonicalize_url(
            self.config.seed_url,
            self.config.seed_url,
            allowed_domains=self.profile.allowed_domains,
            allowed_prefix=self.profile.allowed_path_prefix,
        )
        if not seed:
            raise ValueError(f"URL inicial inválida para o domínio permitido: {self.config.seed_url}")

        if not self.config.resume:
            self.enqueued = {seed}
            return [seed]

        checkpoint = self.storage.load_checkpoint()
        if not checkpoint:
            self.enqueued = {seed}
            return [seed]

        visited = checkpoint.get("visited", [])
        pending = checkpoint.get("pending", [])
        self.visited = {url for url in visited if isinstance(url, str)}
        pending_urls = [url for url in pending if isinstance(url, str) and url not in self.visited]

        self.enqueued = set(self.visited).union(pending_urls)
        previous_stats = checkpoint.get("stats")
        if isinstance(previous_stats, dict):
            for key, value in previous_stats.items():
                if key in self.stats and isinstance(value, int):
                    self.stats[key] = value
        previous_failures = checkpoint.get("failed_pages")
        if isinstance(previous_failures, dict):
            self.failed_pages = {
                str(url): str(reason)
                for url, reason in previous_failures.items()
                if isinstance(url, str) and isinstance(reason, str)
            }

        if pending_urls:
            if self.enqueue_soft_cap is not None:
                pending_urls = pending_urls[: self.enqueue_soft_cap]
            self.logger.info(
                "Retomando de checkpoint: %s visitadas, %s pendentes.",
                len(self.visited),
                len(pending_urls),
            )
            return pending_urls

        self.enqueued.add(seed)
        return [seed]

    async def _persist_runtime_status(self, phase: str | None = None) -> None:
        if phase is not None:
            self.current_phase = phase
        async with self.state_lock:
            stats = dict(self.stats)
            failed_pages = dict(self.failed_pages)
            visited_count = len(self.visited)
            enqueued_count = len(self.enqueued)
            pending_count = len(self.enqueued.difference(self.visited))
        self.storage.write_runtime_status(
            build_runtime_status(
                phase=self.current_phase,
                stats=stats,
                failed_pages=failed_pages,
                visited_count=visited_count,
                enqueued_count=enqueued_count,
                pending_count=pending_count,
                site_profile=self.profile,
                run_config=self.run_config,
            )
        )

    def _persist_runtime_status_now(self, phase: str | None = None) -> None:
        if phase is not None:
            self.current_phase = phase
        self.storage.write_runtime_status(
            build_runtime_status(
                phase=self.current_phase,
                stats=dict(self.stats),
                failed_pages=dict(self.failed_pages),
                visited_count=len(self.visited),
                enqueued_count=len(self.enqueued),
                pending_count=len(self.enqueued.difference(self.visited)),
                site_profile=self.profile,
                run_config=self.run_config,
            )
        )

    async def _load_robots(self, client: httpx.AsyncClient) -> None:
        if not self.config.respect_robots_txt:
            self.robot_rules = None
            return

        domain = self.profile.allowed_domains[0]
        robots_url = f"https://{domain}/robots.txt"
        try:
            await self.rate_limiter.wait()
            response = await client.get(robots_url)
            if response.status_code >= 400:
                self.logger.warning("Não foi possível ler robots.txt (%s)", response.status_code)
                self.robot_rules = None
                return
            parser = robotparser.RobotFileParser()
            parser.parse(response.text.splitlines())
            self.robot_rules = parser
            self.logger.info("robots.txt carregado de %s", robots_url)
        except httpx.HTTPError as exc:
            self.logger.warning("Falha ao carregar robots.txt (%r). Continuando.", exc)
            self.robot_rules = None

    def _finalize_stats(self) -> None:
        finished = datetime.now(UTC)
        started = datetime.fromisoformat(self.stats["started_at"])
        self.stats["finished_at"] = finished.isoformat()
        self.stats["duration_seconds"] = round((finished - started).total_seconds(), 2)


TibiaWikiCrawler = QuickWikiCrawler


def _serialize_html_fragment(soup: BeautifulSoup) -> str:
    if soup.body:
        return "".join(str(child) for child in soup.body.contents)
    return str(soup)


def _extract_template_names_from_wikitext(wikitext: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for match in html.unescape(wikitext).split("{{")[1:]:
        candidate = match.split("}}", maxsplit=1)[0].split("|", maxsplit=1)[0].strip()
        if not candidate:
            continue
        candidate = candidate.lstrip("{").strip()
        candidate = candidate.removeprefix("subst:").removeprefix("Subst:").strip()
        if not candidate or any(symbol in candidate for symbol in "\n[]<>"):
            continue
        if candidate not in seen:
            seen.add(candidate)
            names.append(candidate)
        if len(names) >= 80:
            break
    return names
