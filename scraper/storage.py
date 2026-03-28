from __future__ import annotations

import html
import json
import os
import threading
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import PageDocument
from .presentation import (
    first_health_note,
    humanize_fetch_source_label,
    humanize_health,
    humanize_health_label,
    humanize_public_key,
)
from .reporting import build_run_report, summarize_failed_pages
from .site_profiles import WikiSiteProfile
from .ui_assets import MIRROR_INDEX_JS, build_mirror_css
from .url_utils import extension_from_url, shard_from_slug, slug_from_url
from .version import QUICKWIKI_VERSION, build_artifact_metadata


class StorageManager:
    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root
        self.data_dir = self.output_root / "data"
        self.pages_dir = self.data_dir / "pages"
        self.pages_md_dir = self.pages_dir / "markdown"
        self.pages_json_dir = self.pages_dir / "json"
        self.pages_html_dir = self.pages_dir / "html"
        self.pages_source_dir = self.pages_dir / "source"

        self.assets_dir = self.data_dir / "assets"
        self.static_dir = self.output_root / "static"
        self.admin_dir = self.output_root / "admin"
        self.indexes_dir = self.data_dir / "indexes"
        self.checkpoints_dir = self.output_root / "checkpoints"
        self.logs_dir = self.output_root / "logs"

        self.state_file = self.checkpoints_dir / "state.json"
        self.runtime_status_file = self.checkpoints_dir / "runtime_status.json"
        self.url_to_slug_file = self.indexes_dir / "url_to_slug.json"
        self.assets_by_hash_file = self.indexes_dir / "assets_by_hash.json"
        self.assets_by_url_file = self.indexes_dir / "assets_by_url.json"
        self.pages_manifest_file = self.indexes_dir / "pages_manifest.json"
        self.link_graph_file = self.indexes_dir / "link_graph.json"
        self.backlinks_file = self.indexes_dir / "backlinks.json"
        self.category_index_file = self.indexes_dir / "categories.json"
        self.duplicate_content_file = self.indexes_dir / "duplicate_content.json"
        self.failed_pages_file = self.indexes_dir / "failed_pages.json"
        self.search_index_js_file = self.indexes_dir / "search_index.js"
        self.profile_diagnostics_file = self.indexes_dir / "profile_diagnostics.json"
        self.summary_file = self.indexes_dir / "summary.json"
        self.run_report_file = self.indexes_dir / "run_report.json"
        self.theme_css_file = self.static_dir / "mirror.css"
        self.index_js_file = self.static_dir / "mirror-index.js"

        self._lock = threading.Lock()

        self.url_to_slug: dict[str, str] = {}
        self.assets_by_hash: dict[str, dict[str, Any]] = {}
        self.assets_by_url: dict[str, str] = {}
        self.pages_manifest: dict[str, dict[str, Any]] = {}
        self.link_graph: dict[str, list[str]] = {}

        self._create_dirs()
        self._write_ui_assets()
        self._load_existing_indexes()

    def register_url(self, url: str) -> str:
        with self._lock:
            slug = self.url_to_slug.get(url)
            if slug:
                return slug
            slug = slug_from_url(url)
            self.url_to_slug[url] = slug
            return slug

    def page_paths(self, slug: str) -> dict[str, Path]:
        shard = shard_from_slug(slug)
        markdown_path = self.pages_md_dir / shard / f"{slug}.md"
        json_path = self.pages_json_dir / shard / f"{slug}.json"
        html_path = self.pages_html_dir / shard / f"{slug}.html"
        source_path = self.pages_source_dir / shard / f"{slug}.wiki"
        return {"markdown": markdown_path, "json": json_path, "html": html_path, "source": source_path}

    def html_relative_link(self, from_slug: str, to_slug: str) -> str:
        from_path = self.page_paths(from_slug)["html"].parent
        to_path = self.page_paths(to_slug)["html"]
        return os.path.relpath(to_path, start=from_path).replace("\\", "/")

    def asset_relative_link_from_page(self, from_slug: str, asset_relative_path: str) -> str:
        from_path = self.page_paths(from_slug)["html"].parent
        target = self.output_root / asset_relative_path
        return os.path.relpath(target, start=from_path).replace("\\", "/")

    def static_relative_link_from_page(self, from_slug: str, filename: str) -> str:
        from_path = self.page_paths(from_slug)["html"].parent
        target = self.static_dir / filename
        return os.path.relpath(target, start=from_path).replace("\\", "/")

    def resolve_asset_by_url(self, url: str) -> dict[str, Any] | None:
        with self._lock:
            sha = self.assets_by_url.get(url)
            if not sha:
                return None
            payload = self.assets_by_hash.get(sha)
            if not payload:
                return None
            return payload.copy()

    def persist_asset(
        self,
        *,
        source_url: str,
        content: bytes,
        bucket: str,
        content_type: str | None,
    ) -> dict[str, Any]:
        import hashlib

        digest = hashlib.sha256(content).hexdigest()
        extension = _preferred_extension(source_url, content_type)

        with self._lock:
            existing = self.assets_by_hash.get(digest)
            if existing:
                self.assets_by_url[source_url] = digest
                return existing.copy()

            directory = self.assets_dir / bucket / digest[:2]
            directory.mkdir(parents=True, exist_ok=True)
            file_path = directory / f"{digest}{extension}"
            if not file_path.exists():
                _atomic_write_bytes(file_path, content)

            relative = file_path.relative_to(self.output_root).as_posix()
            payload = {
                "sha256": digest,
                "bucket": bucket,
                "relative_path": relative,
                "bytes": len(content),
                "content_type": content_type or "",
            }
            self.assets_by_hash[digest] = payload
            self.assets_by_url[source_url] = digest
            return payload.copy()

    def alias_asset_url(self, url: str, sha256: str) -> None:
        with self._lock:
            if sha256 in self.assets_by_hash:
                self.assets_by_url[url] = sha256

    def save_page(self, page: PageDocument) -> dict[str, str]:
        paths = self.page_paths(page.slug)
        for path in paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)

        home_relative = os.path.relpath(self.output_root / "index.html", start=paths["html"].parent).replace("\\", "/")
        markdown_payload = _build_markdown_document(page)
        page_payload = page.to_dict()
        page_payload.update(build_artifact_metadata("page_document", generated_at=page.fetched_at))
        _atomic_write_text(paths["markdown"], markdown_payload)
        _atomic_write_text(paths["json"], _to_json(page_payload))
        source_relative = (
            os.path.relpath(paths["source"], start=paths["html"].parent).replace("\\", "/") if page.wikitext else ""
        )
        _atomic_write_text(
            paths["html"],
            _build_html_document(
                page,
                home_relative,
                theme_css_href=self.static_relative_link_from_page(page.slug, "mirror.css"),
                local_source_path_override=source_relative,
            ),
        )
        if page.wikitext:
            _atomic_write_text(paths["source"], page.wikitext)

        with self._lock:
            self.url_to_slug[page.url] = page.slug
            self.link_graph[page.url] = page.internal_links
            self.pages_manifest[page.slug] = {
                "slug": page.slug,
                "title": page.title,
                "url": page.url,
                "excerpt": page.excerpt,
                "word_count": page.word_count,
                "reading_time_minutes": page.reading_time_minutes,
                "fetch_source": page.fetch_source,
                "site_profile": page.site_profile,
                "source_templates": page.source_templates[:40],
                "source_edit_url": page.source_edit_url,
                "source_raw_url": page.source_raw_url,
                "wikitext_characters": len(page.wikitext),
                "categories": page.categories,
                "headings": [heading["text"] for heading in page.headings[:16] if heading.get("text")],
                "content_hash": page.content_hash,
                "internal_links_count": len(page.internal_links),
                "external_links_count": len(page.external_links),
                "images_count": len(page.images),
                "paths": {
                    "html": paths["html"].relative_to(self.output_root).as_posix(),
                    "markdown": paths["markdown"].relative_to(self.output_root).as_posix(),
                    "json": paths["json"].relative_to(self.output_root).as_posix(),
                    "source": (
                        paths["source"].relative_to(self.output_root).as_posix() if page.wikitext else ""
                    ),
                },
            }

        return {
            "markdown": paths["markdown"].as_posix(),
            "json": paths["json"].as_posix(),
            "html": paths["html"].as_posix(),
            "source": paths["source"].as_posix(),
        }

    def save_checkpoint(
        self,
        *,
        visited: set[str],
        pending: set[str],
        stats: dict[str, Any],
        failed_pages: dict[str, str] | None = None,
    ) -> None:
        payload = {
            "saved_at": datetime.now(UTC).isoformat(),
            "visited": sorted(visited),
            "pending": sorted(pending),
            "stats": stats,
            "failed_pages": failed_pages or {},
        }
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(self.state_file, _to_json(payload))
        self.flush_indexes()

    def load_checkpoint(self) -> dict[str, Any] | None:
        if not self.state_file.exists():
            return None
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def write_runtime_status(self, payload: dict[str, Any]) -> None:
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(self.runtime_status_file, _to_json(payload))

    def load_runtime_status(self) -> dict[str, Any] | None:
        if not self.runtime_status_file.exists():
            return None
        try:
            payload = json.loads(self.runtime_status_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    def flush_indexes(self) -> None:
        with self._lock:
            self.indexes_dir.mkdir(parents=True, exist_ok=True)
            _atomic_write_text(self.url_to_slug_file, _to_json(self.url_to_slug))
            _atomic_write_text(self.assets_by_hash_file, _to_json(self.assets_by_hash))
            _atomic_write_text(self.assets_by_url_file, _to_json(self.assets_by_url))
            manifest_entries = sorted(self.pages_manifest.values(), key=lambda entry: entry["title"].lower())
            _atomic_write_text(
                self.pages_manifest_file,
                _to_json(_build_pages_manifest_payload(manifest_entries)),
            )
            _atomic_write_text(self.link_graph_file, _to_json(self.link_graph))

    def finalize(
        self,
        stats: dict[str, Any],
        *,
        failed_pages: dict[str, str] | None = None,
        site_profile: WikiSiteProfile | None = None,
        run_config: dict[str, Any] | None = None,
    ) -> None:
        self.flush_indexes()
        backlinks, category_index, duplicate_content, search_entries = self._build_derived_indexes()
        generated_at = datetime.now(UTC).isoformat()

        failed_summary = summarize_failed_pages(failed_pages or {})
        failed_payload = {
            **build_artifact_metadata("failed_pages", generated_at=generated_at),
            **failed_summary,
            "pages": dict(sorted((failed_pages or {}).items(), key=lambda item: item[0])),
        }
        summary = {
            **build_artifact_metadata("summary", generated_at=generated_at),
            "pages_saved": len(self.pages_manifest),
            "assets_saved": len(self.assets_by_hash),
            "categories_indexed": len(category_index),
            "duplicate_content_groups": len(duplicate_content),
            "failed_pages": failed_payload["count"],
            "site_profile": site_profile.key if site_profile else stats.get("site_profile", ""),
            "site_label": site_profile.label if site_profile else stats.get("site_label", ""),
            "fetch_sources": dict(
                sorted(
                    Counter(entry.get("fetch_source", "unknown") for entry in self.pages_manifest.values()).items()
                )
            ),
            "stats": stats,
        }
        profile_diagnostics = _build_profile_diagnostics(site_profile, summary)
        run_report = build_run_report(
            output_root=self.output_root,
            summary=summary,
            stats=stats,
            failed_pages=failed_pages or {},
            site_profile=site_profile,
            run_config=run_config,
        )

        _atomic_write_text(self.backlinks_file, _to_json(backlinks))
        _atomic_write_text(self.category_index_file, _to_json(category_index))
        _atomic_write_text(self.duplicate_content_file, _to_json(duplicate_content))
        _atomic_write_text(self.failed_pages_file, _to_json(failed_payload))
        _atomic_write_text(self.profile_diagnostics_file, _to_json(profile_diagnostics))
        _atomic_write_text(
            self.search_index_js_file,
            "window.__QUICKWIKI_SEARCH_INDEX__ = " + _to_json(search_entries) + ";\n"
            "window.__TIBIA_WIKI_SEARCH_INDEX__ = window.__QUICKWIKI_SEARCH_INDEX__;\n",
        )
        _atomic_write_text(self.summary_file, _to_json(summary))
        _atomic_write_text(self.run_report_file, _to_json(run_report))
        self._rewrite_page_documents_with_navigation(backlinks)
        self._write_ui_assets(site_profile)
        self._write_landing_page(summary, run_report)
        self._write_admin_page(summary, profile_diagnostics, run_report)

    def _create_dirs(self) -> None:
        for folder in (
            self.output_root,
            self.data_dir,
            self.pages_md_dir,
            self.pages_json_dir,
            self.pages_html_dir,
            self.pages_source_dir,
            self.assets_dir,
            self.static_dir,
            self.admin_dir,
            self.indexes_dir,
            self.checkpoints_dir,
            self.logs_dir,
        ):
            folder.mkdir(parents=True, exist_ok=True)

    def _write_ui_assets(self, site_profile: WikiSiteProfile | None = None) -> None:
        theme = site_profile.theme if site_profile else None
        _atomic_write_text(self.theme_css_file, build_mirror_css(theme) + "\n")
        _atomic_write_text(self.index_js_file, MIRROR_INDEX_JS + "\n")

    def _load_existing_indexes(self) -> None:
        self.url_to_slug = _read_json_dict(self.url_to_slug_file)
        self.assets_by_hash = _read_json_dict(self.assets_by_hash_file)
        self.assets_by_url = _read_json_dict(self.assets_by_url_file)
        manifest_list = _read_json_list(self.pages_manifest_file, data_keys=("pages",))
        self.pages_manifest = {
            entry["slug"]: entry for entry in manifest_list if isinstance(entry, dict) and "slug" in entry
        }
        self.link_graph = _read_json_dict(self.link_graph_file)

    def _build_derived_indexes(
        self,
    ) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]]]:
        manifest_by_url = {
            entry["url"]: entry for entry in self.pages_manifest.values() if isinstance(entry, dict) and "url" in entry
        }

        backlinks: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for source_url, targets in self.link_graph.items():
            source_entry = manifest_by_url.get(source_url)
            if not source_entry:
                continue
            source_preview = _page_reference(source_entry)
            for target_url in targets:
                if target_url not in manifest_by_url:
                    continue
                backlinks[target_url].append(source_preview)

        normalized_backlinks = {
            target_url: sorted(links, key=lambda entry: entry["title"].lower())
            for target_url, links in sorted(backlinks.items())
        }

        category_index: dict[str, list[dict[str, Any]]] = {}
        category_buckets: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in self.pages_manifest.values():
            for category in entry.get("categories", []):
                category_buckets[category].append(_page_reference(entry))
        for category, pages in sorted(category_buckets.items(), key=lambda item: item[0].lower()):
            category_index[category] = sorted(pages, key=lambda entry: entry["title"].lower())

        duplicates_by_hash: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in self.pages_manifest.values():
            content_hash = entry.get("content_hash")
            if isinstance(content_hash, str) and content_hash:
                duplicates_by_hash[content_hash].append(_page_reference(entry))
        duplicate_content = [
            {
                "content_hash": content_hash,
                "pages": sorted(pages, key=lambda entry: entry["title"].lower()),
            }
            for content_hash, pages in duplicates_by_hash.items()
            if len(pages) > 1
        ]
        duplicate_content.sort(key=lambda group: (-len(group["pages"]), group["pages"][0]["title"].lower()))

        search_entries = []
        for entry in sorted(self.pages_manifest.values(), key=lambda item: item["title"].lower()):
            search_entries.append(
                {
                    "title": entry["title"],
                    "slug": entry["slug"],
                    "url": entry["url"],
                    "html_path": entry["paths"]["html"],
                    "excerpt": entry.get("excerpt", ""),
                    "categories": entry.get("categories", []),
                    "headings": entry.get("headings", []),
                    "word_count": entry.get("word_count", 0),
                    "reading_time_minutes": entry.get("reading_time_minutes", 0),
                    "images_count": entry.get("images_count", 0),
                    "internal_links_count": entry.get("internal_links_count", 0),
                    "fetch_source": entry.get("fetch_source", "unknown"),
                    "site_profile": entry.get("site_profile", ""),
                    "source_templates": entry.get("source_templates", []),
                    "wikitext_characters": entry.get("wikitext_characters", 0),
                }
            )

        return normalized_backlinks, category_index, duplicate_content, search_entries

    def _rewrite_page_documents_with_navigation(self, backlinks: dict[str, list[dict[str, Any]]]) -> None:
        manifest_by_url = {
            entry["url"]: entry for entry in self.pages_manifest.values() if isinstance(entry, dict) and "url" in entry
        }
        for entry in self.pages_manifest.values():
            json_path = self.output_root / entry["paths"]["json"]
            html_path = self.output_root / entry["paths"]["html"]
            if not json_path.exists():
                continue

            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            if not isinstance(payload, dict):
                continue

            outgoing = [
                _page_reference(manifest_by_url[target_url], from_dir=html_path.parent, output_root=self.output_root)
                for target_url in self.link_graph.get(entry["url"], [])
                if target_url in manifest_by_url
            ][:18]
            incoming = [
                _page_reference(manifest_by_url[link["url"]], from_dir=html_path.parent, output_root=self.output_root)
                for link in backlinks.get(entry["url"], [])
                if link.get("url") in manifest_by_url
            ][:18]
            external_links = [
                link for link in payload.get("external_links", []) if isinstance(link, str) and link.strip()
            ][:8]
            home_relative = os.path.relpath(self.output_root / "index.html", start=html_path.parent).replace("\\", "/")
            _atomic_write_text(
                html_path,
                _build_html_document(
                    payload,
                    home_relative,
                    theme_css_href=os.path.relpath(self.theme_css_file, start=html_path.parent).replace("\\", "/"),
                    outgoing_links=outgoing,
                    incoming_links=incoming,
                    featured_external_links=external_links,
                    local_source_path_override=(
                        os.path.relpath(self.output_root / entry["paths"]["source"], start=html_path.parent).replace(
                            "\\",
                            "/",
                        )
                        if entry["paths"].get("source")
                        else ""
                    ),
                ),
            )

    def _write_landing_page(self, summary: dict[str, Any], run_report: dict[str, Any]) -> None:
        health = run_report.get("health", {}) if isinstance(run_report.get("health"), dict) else {}
        health_status = humanize_health(str(health.get("status", "ok")))
        health_note = first_health_note(health)
        version = html.escape(str(summary.get("quickwiki_version", QUICKWIKI_VERSION)))
        page = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>QuickWiki</title>
  <link rel="stylesheet" href="static/mirror.css">
  <script src="data/indexes/search_index.js"></script>
  <script src="static/mirror-index.js"></script>
</head>
<body>
  <main class="mirror-shell">
    <section class="mirror-hero">
      <span class="mirror-eyebrow">Seu espelho offline</span>
      <div>
        <h1 class="mirror-title">QuickWiki</h1>
        <p class="mirror-meta-line">
          Esta copia local esta pronta para leitura, busca e consulta sem depender do site original.
        </p>
        <p class="mirror-meta-line"><strong>Versao:</strong> {version}</p>
        <p class="mirror-meta-line"><strong>Perfil em uso:</strong> {html.escape(str(summary.get("site_label") or summary.get("site_profile") or "desconhecido"))}</p>
        <p class="mirror-meta-line"><strong>Resumo da execucao:</strong> {html.escape(health_status)}{(" | " + html.escape(health_note)) if health_note else ""}</p>
      </div>
      <div class="mirror-summary">
        <div class="mirror-stat"><strong>{summary["pages_saved"]}</strong>Paginas salvas</div>
        <div class="mirror-stat"><strong>{summary["assets_saved"]}</strong>Arquivos unicos</div>
        <div class="mirror-stat"><strong>{summary["categories_indexed"]}</strong>Categorias</div>
        <div class="mirror-stat"><strong>{summary["failed_pages"]}</strong>Pendencias</div>
      </div>
      <div class="mirror-controls">
        <label>
          <input class="mirror-input" id="search" placeholder="Buscar por titulo, trecho, categoria ou assunto..." autocomplete="off">
        </label>
        <label>
          <select class="mirror-select" id="category">
            <option value="">Todas as categorias</option>
          </select>
        </label>
      </div>
      <div class="mirror-links">
        <a href="data/indexes/pages_manifest.json">Lista completa de paginas</a>
        <a href="data/indexes/backlinks.json">Links entre paginas</a>
        <a href="data/indexes/categories.json">Categorias</a>
        <a href="data/indexes/duplicate_content.json">Conteudos parecidos</a>
        <a href="data/indexes/failed_pages.json">Paginas com falha</a>
        <a href="data/indexes/run_report.json">Detalhes da execucao</a>
        <a href="checkpoints/runtime_status.json">Status da execucao</a>
        <a href="admin/index.html">Area tecnica</a>
      </div>
      <div class="mirror-meta-line">Gerado em {html.escape(summary["generated_at"])}</div>
    </section>

    <div class="mirror-toolbar">
      <div class="mirror-result-count" id="result-count">Preparando lista de paginas...</div>
    </div>

    <section class="mirror-results" id="results"></section>
  </main>
  <script>window.QuickWikiApp && window.QuickWikiApp.bootIndex();</script>
</body>
</html>
"""
        _atomic_write_text(self.output_root / "index.html", page)

    def _write_admin_page(
        self,
        summary: dict[str, Any],
        profile_diagnostics: dict[str, Any],
        run_report: dict[str, Any],
    ) -> None:
        profile = profile_diagnostics.get("profile", {})
        selectors = profile_diagnostics.get("selectors", {})
        theme = profile_diagnostics.get("theme", {})
        files = profile_diagnostics.get("files", {})
        stats = profile_diagnostics.get("stats", {})
        health = run_report.get("health", {}) if isinstance(run_report.get("health"), dict) else {}

        selector_sections = "".join(
            f"""
            <section class="mirror-admin-card">
              <h2>{html.escape(_humanize_key(name))}</h2>
              <small>{len(values)} regra(s) configurada(s)</small>
              <code class="mirror-admin-code">{html.escape("\n".join(values) or "Nenhuma regra configurada.")}</code>
            </section>
            """
            for name, values in selectors.items()
            if isinstance(values, list)
        )
        if not selector_sections:
            selector_sections = """
            <section class="mirror-admin-card">
              <h2>Regras do perfil</h2>
              <div class="mirror-empty">Nenhuma regra foi registrada para este perfil.</div>
            </section>
            """

        theme_chips = "".join(
            f'<span class="mirror-chip">{html.escape(key)}: {html.escape(value)}</span>'
            for key, value in sorted(theme.items())
        ) or '<span class="mirror-chip">Sem ajuste visual extra</span>'
        file_rows = "".join(
            f'<li><strong>{html.escape(_humanize_key(key))}:</strong> '
            f'<a href="{html.escape(_admin_file_href(str(value)))}">{html.escape(str(value))}</a></li>'
            for key, value in files.items()
            if value
        )
        stat_rows = "".join(
            f'<div class="mirror-stat"><strong>{html.escape(str(value))}</strong>{html.escape(_humanize_key(key))}</div>'
            for key, value in stats.items()
        )
        health_rows = _build_health_rows(health)

        page = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Visao tecnica do espelho</title>
  <link rel="stylesheet" href="../static/mirror.css">
</head>
<body>
  <main class="mirror-shell">
    <section class="mirror-hero">
      <span class="mirror-eyebrow">Area tecnica</span>
      <div>
        <h1 class="mirror-title">Visao tecnica do espelho</h1>
        <p class="mirror-meta-line">
          Esta area reune o perfil usado, os arquivos principais e os sinais mais importantes da ultima execucao.
        </p>
      </div>
      <p class="mirror-meta-line"><strong>Versao:</strong> {html.escape(str(summary.get("quickwiki_version", QUICKWIKI_VERSION)))}</p>
      <p class="mirror-meta-line"><strong>Perfis oficiais:</strong> os perfis incluidos no projeto ja estao prontos para uso. Perfis extras continuam disponiveis pela CLI.</p>
      <div class="mirror-summary">
        <div class="mirror-stat"><strong>{html.escape(str(summary.get("pages_saved", 0)))}</strong>Paginas</div>
        <div class="mirror-stat"><strong>{html.escape(str(summary.get("assets_saved", 0)))}</strong>Arquivos</div>
        <div class="mirror-stat"><strong>{html.escape(str(summary.get("failed_pages", 0)))}</strong>Pendencias</div>
        <div class="mirror-stat"><strong>{html.escape(str(stats.get("source_pages_captured", 0)))}</strong>Paginas com codigo</div>
      </div>
      <div class="mirror-admin-actions">
        <a href="../index.html">Abrir pagina inicial</a>
        <a href="../data/indexes/profile_diagnostics.json">Diagnostico do perfil</a>
        <a href="../data/indexes/summary.json">Resumo da execucao</a>
        <a href="../data/indexes/run_report.json">Detalhes da execucao</a>
        <a href="../data/indexes/pages_manifest.json">Lista de paginas</a>
      </div>
    </section>

    <section class="mirror-admin-grid" style="margin-top:18px">
      <section class="mirror-admin-card">
        <h2>Perfil em uso</h2>
        <small>Identidade, origem e regras principais do perfil carregado.</small>
        <code class="mirror-admin-code">{html.escape(_format_profile_block(profile))}</code>
      </section>
      <section class="mirror-admin-card">
        <h2>Tema</h2>
        <small>Cores e sinais visuais usados neste espelho.</small>
        <div class="mirror-chips">{theme_chips}</div>
      </section>
      <section class="mirror-admin-card">
        <h2>Arquivos uteis</h2>
        <small>Atalhos para revisar a saida gerada.</small>
        <ul class="mirror-link-list">{file_rows or '<li>Nenhum arquivo adicional registrado.</li>'}</ul>
      </section>
      <section class="mirror-admin-card">
        <h2>Resumo da execucao</h2>
        <small>Sinais rapidos da ultima rodada salva.</small>
        <code class="mirror-admin-code">{html.escape(_format_run_health_block(health))}</code>
      </section>
    </section>

    <section class="mirror-toolbar">
      <div class="mirror-result-count">Visao tecnica do espelho e do perfil escolhido</div>
    </section>

    <section class="mirror-summary" style="margin-bottom:18px">
      {stat_rows}
    </section>

    <section class="mirror-admin-grid" style="margin-bottom:18px">
      {health_rows}
    </section>

    <section class="mirror-admin-grid">
      {selector_sections}
    </section>
  </main>
</body>
</html>
"""
        _atomic_write_text(self.admin_dir / "index.html", page)


def _build_markdown_document(page: PageDocument) -> str:
    header = {
        "quickwiki_version": QUICKWIKI_VERSION,
        "schema_version": 1,
        "title": page.title,
        "source_url": page.url,
        "fetched_at": page.fetched_at,
        "slug": page.slug,
        "site_profile": page.site_profile,
        "excerpt": page.excerpt,
        "word_count": page.word_count,
        "reading_time_minutes": page.reading_time_minutes,
        "fetch_source": page.fetch_source,
        "source_edit_url": page.source_edit_url,
        "source_raw_url": page.source_raw_url,
        "source_templates": page.source_templates,
        "categories": page.categories,
    }
    frontmatter_lines = ["---"]
    for key, value in header.items():
        if isinstance(value, list):
            serialized = ", ".join(value)
        else:
            serialized = str(value)
        frontmatter_lines.append(f"{key}: {serialized}")
    frontmatter_lines.append("---")
    return "\n".join(frontmatter_lines) + "\n\n" + page.markdown.strip() + "\n"


def _build_html_document(
    page: PageDocument | dict[str, Any],
    home_relative: str,
    *,
    theme_css_href: str,
    outgoing_links: list[dict[str, Any]] | None = None,
    incoming_links: list[dict[str, Any]] | None = None,
    featured_external_links: list[str] | None = None,
    local_source_path_override: str = "",
) -> str:
    payload = page.to_dict() if isinstance(page, PageDocument) else page
    title_text = str(payload.get("title", "Sem titulo"))
    source_url_text = str(payload.get("url", ""))
    categories_list = [
        str(category) for category in payload.get("categories", []) if isinstance(category, str) and category.strip()
    ]
    excerpt_text = str(payload.get("excerpt") or "Sem resumo disponivel ainda.")
    fetched_at = str(payload.get("fetched_at", ""))
    fetch_source = humanize_fetch_source_label(str(payload.get("fetch_source", "unknown")))
    source_edit_url_text = str(payload.get("source_edit_url", ""))
    source_raw_url_text = str(payload.get("source_raw_url", ""))
    source_templates = [
        str(name) for name in payload.get("source_templates", []) if isinstance(name, str) and name.strip()
    ]
    word_count = int(payload.get("word_count", 0) or 0)
    reading_time = int(payload.get("reading_time_minutes", 0) or 0)
    images_count = len(payload.get("images", [])) if isinstance(payload.get("images"), list) else 0
    wikitext_characters = len(str(payload.get("wikitext", ""))) or int(payload.get("wikitext_characters", 0) or 0)
    html_clean = str(payload.get("html_clean", ""))

    title = html.escape(title_text)
    source_url = html.escape(source_url_text)
    categories = "".join(f'<span class="mirror-chip">{html.escape(category)}</span>' for category in categories_list) or (
        '<span class="mirror-chip">Sem categorias registradas</span>'
    )
    excerpt = html.escape(excerpt_text)
    outgoing_section = _build_link_section("Links desta pagina", outgoing_links or [], is_external=False)
    incoming_section = _build_link_section("Paginas que apontam para ca", incoming_links or [], is_external=False)
    external_section = _build_link_section(
        "Links externos",
        [{"title": link, "url": link} for link in (featured_external_links or [])],
        is_external=True,
    )
    source_section = _build_source_section(
        source_edit_url=source_edit_url_text,
        source_raw_url=source_raw_url_text,
        source_templates=source_templates,
        wikitext_characters=wikitext_characters,
        local_source_path=local_source_path_override
        or (str(payload.get("paths", {}).get("source", "")) if isinstance(payload.get("paths"), dict) else ""),
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{html.escape(theme_css_href)}">
</head>
<body class="mirror-page">
  <div class="mirror-page-shell">
    <div class="mirror-topbar">
      <a href="{html.escape(home_relative)}">Voltar para o espelho</a>
      <a href="{source_url}">Abrir original online</a>
    </div>
    <h1 class="mirror-page-title">{title}</h1>
    <div class="mirror-meta">
      <div class="mirror-excerpt">{excerpt}</div>
      <div><strong>Pagina original:</strong> <a href="{source_url}">{source_url}</a></div>
      <div><strong>Salvo em:</strong> {html.escape(fetched_at)} | <strong>Como esta pagina foi coletada:</strong> {html.escape(fetch_source)}</div>
      <div><strong>Tamanho estimado:</strong> {word_count} palavras | <strong>Leitura:</strong> {reading_time} min | <strong>Imagens:</strong> {images_count} | <strong>Texto-fonte:</strong> {wikitext_characters} chars</div>
      <div class="mirror-chips">{categories}</div>
    </div>
    <div class="mirror-layout">
      <article class="mirror-content-card">
        {html_clean}
      </article>
      <aside class="mirror-sidebar">
        {source_section}
        {outgoing_section}
        {incoming_section}
        {external_section}
      </aside>
    </div>
  </div>
</body>
</html>
"""


def _build_link_section(title: str, entries: list[dict[str, Any]], *, is_external: bool) -> str:
    if not entries:
        return (
            f'<section class="mirror-side-card"><h2>{html.escape(title)}</h2>'
            '<div class="mirror-side-empty">Nenhum link disponivel.</div></section>'
        )

    rows = []
    for entry in entries:
        label = html.escape(str(entry.get("title") or entry.get("url") or "Sem titulo"))
        target = str(entry.get("url") or "")
        href = entry.get("html_path") if not is_external else target
        if not isinstance(href, str) or not href:
            continue
        note = html.escape(target) if is_external else html.escape(target)
        rows.append(f'<li><a href="{html.escape(href)}">{label}</a><br><small>{note}</small></li>')
    if not rows:
        return (
            f'<section class="mirror-side-card"><h2>{html.escape(title)}</h2>'
            '<div class="mirror-side-empty">Nenhum link disponivel.</div></section>'
        )
    return (
        f'<section class="mirror-side-card"><h2>{html.escape(title)}</h2>'
        f'<ul class="mirror-link-list">{"".join(rows)}</ul></section>'
    )


def _build_source_section(
    *,
    source_edit_url: str,
    source_raw_url: str,
    source_templates: list[str],
    wikitext_characters: int,
    local_source_path: str,
) -> str:
    links: list[str] = []
    if local_source_path:
        links.append(f'<li><a href="{html.escape(local_source_path)}">Abrir copia local do texto-fonte</a></li>')
    if source_edit_url:
        links.append(f'<li><a href="{html.escape(source_edit_url)}">Ver texto-fonte na wiki</a></li>')
    if source_raw_url:
        links.append(f'<li><a href="{html.escape(source_raw_url)}">Abrir versao bruta</a></li>')

    template_chips = "".join(
        f'<span class="mirror-chip">{html.escape(template_name)}</span>' for template_name in source_templates[:12]
    ) or '<span class="mirror-chip">Sem modelos detectados</span>'
    links_markup = (
        f'<ul class="mirror-link-list">{"".join(links)}</ul>'
        if links
        else '<div class="mirror-side-empty">Nenhum atalho de texto-fonte disponivel.</div>'
    )
    return (
        '<section class="mirror-side-card"><h2>Codigo-fonte da wiki</h2>'
        f'<div class="mirror-side-empty">{wikitext_characters} caracteres salvos do texto-fonte desta pagina.</div>'
        f"{links_markup}"
        f'<div class="mirror-chips" style="margin-top:10px">{template_chips}</div>'
        "</section>"
    )


def _build_profile_diagnostics(
    site_profile: WikiSiteProfile | None,
    summary: dict[str, Any],
) -> dict[str, Any]:
    stats = summary.get("stats", {}) if isinstance(summary.get("stats"), dict) else {}
    if site_profile is None:
        profile_payload: dict[str, Any] = {
            "schema_version": 0,
            "wiki_family": "unknown",
            "key": summary.get("site_profile", ""),
            "label": summary.get("site_label", ""),
            "description": "",
            "default_seed_url": "",
            "allowed_domains": [],
            "allowed_path_prefix": "",
            "api_path": "",
            "definition_path": "",
        }
        selectors_payload: dict[str, list[str]] = {}
        theme_payload: dict[str, str] = {}
    else:
        profile_payload = {
            "schema_version": site_profile.schema_version,
            "wiki_family": site_profile.wiki_family,
            "key": site_profile.key,
            "label": site_profile.label,
            "description": site_profile.description,
            "default_seed_url": site_profile.default_seed_url,
            "allowed_domains": list(site_profile.allowed_domains),
            "allowed_path_prefix": site_profile.allowed_path_prefix,
            "api_path": site_profile.api_path,
            "definition_path": site_profile.definition_path,
        }
        selectors_payload = {
            "title_selectors": list(site_profile.title_selectors),
            "content_root_selectors": list(site_profile.content_root_selectors),
            "category_selectors": list(site_profile.category_selectors),
            "extra_noise_selectors": list(site_profile.extra_noise_selectors),
        }
        theme_payload = dict(site_profile.theme)

    generated_at = str(summary.get("generated_at", ""))
    return {
        **build_artifact_metadata("profile_diagnostics", generated_at=generated_at),
        "profile": profile_payload,
        "selectors": selectors_payload,
        "theme": theme_payload,
        "files": {
            "summary": "data/indexes/summary.json",
            "run_report": "data/indexes/run_report.json",
            "profile_diagnostics": "data/indexes/profile_diagnostics.json",
            "manifest": "data/indexes/pages_manifest.json",
            "search_index": "data/indexes/search_index.js",
            "runtime_status": "checkpoints/runtime_status.json",
            "admin_page": "admin/index.html",
            "landing_page": "index.html",
        },
        "stats": {
            "pages_saved": summary.get("pages_saved", 0),
            "assets_saved": summary.get("assets_saved", 0),
            "categories_indexed": summary.get("categories_indexed", 0),
            "duplicate_content_groups": summary.get("duplicate_content_groups", 0),
            "failed_pages": summary.get("failed_pages", 0),
            "pages_attempted": stats.get("pages_attempted", 0),
            "links_discovered": stats.get("links_discovered", 0),
            "source_pages_captured": stats.get("source_pages_captured", 0),
        },
    }


def _build_pages_manifest_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    generated_at = datetime.now(UTC).isoformat()
    return {
        **build_artifact_metadata("pages_manifest", generated_at=generated_at),
        "pages": entries,
    }


def _page_reference(
    entry: dict[str, Any],
    *,
    from_dir: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, Any]:
    html_path = entry["paths"]["html"]
    if from_dir is not None and output_root is not None:
        html_path = os.path.relpath(output_root / html_path, start=from_dir).replace("\\", "/")
    return {
        "title": entry["title"],
        "slug": entry["slug"],
        "url": entry["url"],
        "html_path": html_path,
    }


def _humanize_key(value: str) -> str:
    return humanize_public_key(value)


def _format_run_health_block(health: dict[str, Any]) -> str:
    warnings = health.get("warnings", []) if isinstance(health.get("warnings"), list) else []
    notes = health.get("notes", []) if isinstance(health.get("notes"), list) else []
    metrics = health.get("metrics", {}) if isinstance(health.get("metrics"), dict) else {}
    rows = [f"situacao: {humanize_health_label(str(health.get('status', 'ok')))}"]
    rows.append(f"taxa_de_falhas: {metrics.get('failure_rate', 0)}")
    rows.append(f"cobertura_codigo_fonte: {metrics.get('source_capture_rate', 0)}")
    rows.append(f"recuperacao_novas_tentativas: {metrics.get('retry_recovery_rate', 0)}")
    rows.append("alertas: " + (" | ".join(str(value) for value in warnings) if warnings else "nenhum"))
    rows.append("observacoes: " + (" | ".join(str(value) for value in notes) if notes else "nenhuma"))
    return "\n".join(rows)


def _build_health_rows(health: dict[str, Any]) -> str:
    rows: list[str] = []
    for label, values in (("Alertas", health.get("warnings", [])), ("Notas", health.get("notes", []))):
        entries = values if isinstance(values, list) else []
        if not entries:
            entries = ["Nenhum item registrado."]
        rows.append(
            f"""
            <section class="mirror-admin-card">
              <h2>{html.escape(label)}</h2>
              <ul class="mirror-link-list">{"".join(f"<li>{html.escape(str(item))}</li>" for item in entries)}</ul>
            </section>
            """
        )
    return "".join(rows)


def _format_profile_block(profile: dict[str, Any]) -> str:
    rows = []
    for key in (
        "schema_version",
        "wiki_family",
        "key",
        "label",
        "description",
        "default_seed_url",
        "allowed_path_prefix",
        "api_path",
        "definition_path",
    ):
        rows.append(f"{humanize_public_key(key)}: {profile.get(key, '')}")
    domains = profile.get("allowed_domains", [])
    rows.append("Dominios permitidos: " + ", ".join(str(domain) for domain in domains))
    return "\n".join(rows)


def _admin_file_href(path_value: str) -> str:
    normalized = path_value.replace("\\", "/")
    if normalized.startswith(("http://", "https://", "../")):
        return normalized
    if normalized.startswith("admin/"):
        return normalized.removeprefix("admin/")
    return f"../{normalized}"


def _preferred_extension(source_url: str, content_type: str | None) -> str:
    from_url = extension_from_url(source_url)
    if from_url != ".bin":
        return from_url

    if not content_type:
        return ".bin"

    normalized = content_type.lower().split(";", maxsplit=1)[0].strip()
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    return mapping.get(normalized, ".bin")


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_bytes(content)
    temp_path.replace(path)


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def _to_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _read_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_json_list(path: Path, *, data_keys: tuple[str, ...] = ()) -> list[Any]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in data_keys:
            candidate = payload.get(key)
            if isinstance(candidate, list):
                return candidate
    return []
