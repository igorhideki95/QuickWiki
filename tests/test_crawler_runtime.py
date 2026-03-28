from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

import httpx

from scraper import QuickWikiCrawler, ScraperConfig
from scraper.models import PageDocument
from scraper.version import QUICKWIKI_VERSION


class CrawlerRuntimeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="quickwiki-crawler-tests-"))
        self.profiles_dir = Path(__file__).resolve().parent.parent / "profiles"
        self.seed_url = "https://www.tibiawiki.com.br/wiki/Home"
        self.config = ScraperConfig(
            seed_url=self.seed_url,
            site_profile="tibiawiki_br",
            profiles_dir=self.profiles_dir,
            output_dir=self.tempdir / "output",
            workers=1,
            asset_workers_per_page=1,
            max_retries=0,
            resume=True,
        )
        self.crawler = QuickWikiCrawler(self.config)

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir, ignore_errors=True)

    async def test_fetch_page_content_returns_direct_html_payload(self) -> None:
        response = httpx.Response(
            200,
            text="<html><body><h1>Home</h1></body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
            request=httpx.Request("GET", self.seed_url),
        )
        self.crawler._fetch_page_http = AsyncMock(return_value=response)
        self.crawler._fetch_page_via_api = AsyncMock()

        payload, failure_reason = await self.crawler._fetch_page_content(object(), self.seed_url)

        self.assertIsNone(failure_reason)
        self.assertEqual(payload["source"], "direct_http")
        self.assertEqual(payload["final_url"], self.seed_url)
        self.crawler._fetch_page_via_api.assert_not_awaited()

    async def test_fetch_page_content_falls_back_to_api_for_non_html_response(self) -> None:
        response = httpx.Response(
            200,
            text='{"ok": true}',
            headers={"content-type": "application/json"},
            request=httpx.Request("GET", self.seed_url),
        )
        fallback_payload = {
            "html": "<html><body><h1>Home</h1></body></html>",
            "encoding": "utf-8",
            "final_url": self.seed_url,
            "title": "Home",
            "source": "mediawiki_api",
        }
        self.crawler._fetch_page_http = AsyncMock(return_value=response)
        self.crawler._fetch_page_via_api = AsyncMock(return_value=fallback_payload)

        payload, failure_reason = await self.crawler._fetch_page_content(object(), self.seed_url)

        self.assertIsNone(failure_reason)
        self.assertEqual(payload, fallback_payload)
        self.crawler._fetch_page_via_api.assert_awaited_once()

    async def test_fetch_page_source_extracts_wikitext_and_templates(self) -> None:
        api_payload = {
            "query": {
                "pages": [
                    {
                        "title": "Amber Sabre",
                        "revisions": [
                            {
                                "slots": {
                                    "main": {
                                        "content": "{{Item|name=Amber Sabre}}\n{{Infobox Creature|name=Dragon}}"
                                    }
                                }
                            }
                        ],
                    }
                ]
            }
        }
        response = httpx.Response(
            200,
            content=json.dumps(api_payload).encode("utf-8"),
            headers={"content-type": "application/json"},
            request=httpx.Request("GET", self.crawler.profile.api_url()),
        )
        self.crawler._fetch_with_retry = AsyncMock(return_value=response)

        payload = await self.crawler._fetch_page_source(
            object(),
            {"title": "Amber Sabre", "final_url": "https://www.tibiawiki.com.br/wiki/Amber_Sabre"},
            "https://www.tibiawiki.com.br/wiki/Amber_Sabre",
        )

        self.assertIsNotNone(payload)
        self.assertEqual(payload["title"], "Amber Sabre")
        self.assertIn("{{Item|name=Amber Sabre}}", payload["wikitext"])
        self.assertEqual(payload["source_templates"][:2], ["Item", "Infobox Creature"])
        self.assertTrue(payload["source_edit_url"].endswith("Amber_Sabre&action=edit"))
        self.assertTrue(payload["source_raw_url"].endswith("Amber_Sabre&action=raw"))

    async def test_fetch_page_via_api_uses_profile_allowed_path_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            profiles_dir = Path(tempdir)
            (profiles_dir / "custom_profile.json").write_text(
                json.dumps(
                    {
                        "key": "custom_profile",
                        "label": "Custom Profile",
                        "description": "Perfil com prefixo nao padrao.",
                        "default_seed_url": "https://example.com/articles/Home",
                        "allowed_domains": ["example.com"],
                        "allowed_path_prefix": "/articles/",
                    }
                ),
                encoding="utf-8",
            )
            crawler = QuickWikiCrawler(
                ScraperConfig(
                    seed_url="https://example.com/articles/Home",
                    site_profile="custom_profile",
                    profiles_dir=profiles_dir,
                    output_dir=self.tempdir / "custom-output",
                    workers=1,
                    asset_workers_per_page=1,
                    max_retries=0,
                )
            )
            api_payload = {
                "parse": {
                    "title": "Test Page",
                    "text": {"*": "<p>Conteudo</p>"},
                    "links": [{"*": "Linked Page"}],
                    "categories": [{"*": "Rare Loot"}],
                    "templates": [{"*": "Infobox"}],
                }
            }
            response = httpx.Response(
                200,
                content=json.dumps(api_payload).encode("utf-8"),
                headers={"content-type": "application/json"},
                request=httpx.Request("GET", crawler.profile.api_url()),
            )
            crawler._fetch_with_retry = AsyncMock(return_value=response)

            payload = await crawler._fetch_page_via_api(object(), "https://example.com/articles/Home")

        self.assertIsNotNone(payload)
        self.assertEqual(payload["final_url"], "https://example.com/articles/Test_Page")
        self.assertEqual(payload["api_links"], ["https://example.com/articles/Linked_Page"])
        self.assertIn("Rare Loot", payload["html"])
        self.assertNotIn("/wiki/", payload["html"])
        self.assertNotIn("Categoria:", payload["html"])

    async def test_bootstrap_from_mediawiki_api_uses_profile_allowed_path_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            profiles_dir = Path(tempdir)
            (profiles_dir / "custom_profile.json").write_text(
                json.dumps(
                    {
                        "key": "custom_profile",
                        "label": "Custom Profile",
                        "description": "Perfil com prefixo nao padrao.",
                        "default_seed_url": "https://example.com/articles/Home",
                        "allowed_domains": ["example.com"],
                        "allowed_path_prefix": "/articles/",
                    }
                ),
                encoding="utf-8",
            )
            crawler = QuickWikiCrawler(
                ScraperConfig(
                    seed_url="https://example.com/articles/Home",
                    site_profile="custom_profile",
                    profiles_dir=profiles_dir,
                    output_dir=self.tempdir / "bootstrap-output",
                    workers=1,
                    asset_workers_per_page=1,
                    max_retries=0,
                    max_pages=None,
                )
            )
            response = httpx.Response(
                200,
                content=json.dumps({"query": {"allpages": [{"title": "Linked Page"}]}}).encode("utf-8"),
                headers={"content-type": "application/json"},
                request=httpx.Request("GET", crawler.profile.api_url()),
            )
            crawler._discover_namespace_ids = AsyncMock(return_value=[0])
            crawler._fetch_with_retry = AsyncMock(return_value=response)

            await crawler._bootstrap_from_mediawiki_api(object())

        self.assertIn("https://example.com/articles/Linked_Page", crawler.enqueued)

    async def test_enqueue_new_urls_deduplicates_and_respects_soft_cap(self) -> None:
        self.crawler.enqueue_soft_cap = 2
        self.crawler.visited = {self.seed_url}
        self.crawler.enqueued = {self.seed_url}
        first = "https://www.tibiawiki.com.br/wiki/Thais"
        second = "https://www.tibiawiki.com.br/wiki/Carlin"
        third = "https://www.tibiawiki.com.br/wiki/Kazordoon"

        discovered = await self.crawler._enqueue_new_urls([first, first, second, third])

        self.assertEqual(discovered, 2)
        self.assertEqual(self.crawler.queue.qsize(), 2)
        self.assertEqual(self.crawler.enqueued, {self.seed_url, first, second})

    async def test_requeue_failed_pages_for_retry_updates_queue_and_stats(self) -> None:
        url_a = "https://www.tibiawiki.com.br/wiki/Teste_A"
        url_b = "https://www.tibiawiki.com.br/wiki/Teste_B"
        self.crawler.failed_pages = {url_a: "http_500", url_b: "http_429"}
        self.crawler.visited = {url_a, url_b}

        requeued = await self.crawler._requeue_failed_pages_for_retry(2)

        self.assertEqual(requeued, 2)
        self.assertEqual(self.crawler.queue.qsize(), 2)
        self.assertNotIn(url_a, self.crawler.visited)
        self.assertNotIn(url_b, self.crawler.visited)
        self.assertEqual(self.crawler.stats["pages_retried"], 2)
        self.assertEqual(self.crawler.stats["retry_rounds_completed"], 2)

    def test_bootstrap_state_restores_checkpoint_metadata(self) -> None:
        seed = self.seed_url
        pending_a = "https://www.tibiawiki.com.br/wiki/Teste_A"
        pending_b = "https://www.tibiawiki.com.br/wiki/Teste_B"
        self.crawler.storage.save_checkpoint(
            visited={seed},
            pending={pending_a, pending_b},
            stats={"pages_saved": 3, "pages_failed": 1},
            failed_pages={pending_b: "http_500"},
        )
        self.crawler.enqueue_soft_cap = 1

        pending = self.crawler._bootstrap_state()

        self.assertEqual(pending, [pending_a])
        self.assertEqual(self.crawler.visited, {seed})
        self.assertEqual(self.crawler.failed_pages, {pending_b: "http_500"})
        self.assertEqual(self.crawler.stats["pages_saved"], 3)
        self.assertEqual(self.crawler.stats["pages_failed"], 1)

    def test_rewrite_asset_links_updates_html_markdown_and_hash(self) -> None:
        page = PageDocument(
            url="https://www.tibiawiki.com.br/wiki/Dragon",
            slug="Dragon--slug",
            title="Dragon",
            html_clean=(
                '<div><img src="https://static.wikia.nocookie.net/tibia/images/thumb/a/ab/Dragon.gif/120px-Dragon.gif" '
                'data-original-src="https://static.wikia.nocookie.net/tibia/images/a/ab/Dragon.gif"></div>'
            ),
            markdown="before",
            content_hash="before",
        )
        stored_relative = "data/assets/monsters/ab/dragon.gif"
        expected_src = self.crawler.storage.asset_relative_link_from_page(page.slug, stored_relative)

        self.crawler._rewrite_asset_links(
            page,
            {"https://static.wikia.nocookie.net/tibia/images/a/ab/Dragon.gif": stored_relative},
        )

        self.assertIn(expected_src, page.html_clean)
        self.assertIn('data-original-src="https://static.wikia.nocookie.net/tibia/images/a/ab/Dragon.gif"', page.html_clean)
        self.assertNotEqual(page.markdown, "before")
        self.assertNotEqual(page.content_hash, "before")

    def test_persist_runtime_status_writes_versioned_public_payload(self) -> None:
        self.crawler.stats["pages_saved"] = 3
        self.crawler.stats["pages_attempted"] = 4
        self.crawler.failed_pages = {"https://www.tibiawiki.com.br/wiki/Falha": "http_429"}
        self.crawler.visited = {
            self.seed_url,
            "https://www.tibiawiki.com.br/wiki/Thais",
        }
        self.crawler.enqueued = {
            self.seed_url,
            "https://www.tibiawiki.com.br/wiki/Thais",
            "https://www.tibiawiki.com.br/wiki/Kazordoon",
        }

        self.crawler._persist_runtime_status_now("crawling")

        runtime_payload = json.loads(
            (self.config.output_dir / "checkpoints" / "runtime_status.json").read_text(encoding="utf-8")
        )
        self.assertEqual(runtime_payload["schema_version"], 1)
        self.assertEqual(runtime_payload["quickwiki_version"], QUICKWIKI_VERSION)
        self.assertEqual(runtime_payload["product"]["version"], QUICKWIKI_VERSION)
        self.assertEqual(runtime_payload["phase"], "crawling")
        self.assertEqual(runtime_payload["queue"]["pending"], 1)


if __name__ == "__main__":
    unittest.main()
