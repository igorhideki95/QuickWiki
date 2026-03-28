from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scraper.models import PageDocument
from scraper.site_profiles import resolve_site_profile
from scraper.storage import StorageManager
from scraper.version import QUICKWIKI_VERSION


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="quickwiki-tests-"))
        self.storage = StorageManager(self.tempdir)

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_finalize_rewrites_pages_with_navigation(self) -> None:
        profile = resolve_site_profile("tibiawiki_br", None)
        url_a = "https://www.tibiawiki.com.br/wiki/Teste_A"
        url_b = "https://www.tibiawiki.com.br/wiki/Teste_B"
        slug_a = self.storage.register_url(url_a)
        slug_b = self.storage.register_url(url_b)

        page_a = PageDocument(
            url=url_a,
            slug=slug_a,
            title="Teste A",
            excerpt="Resumo A",
            word_count=100,
            reading_time_minutes=1,
            internal_links=[url_b],
            external_links=["https://example.com/a"],
            html_clean="<div><p>Conteudo A</p></div>",
            markdown="Conteudo A",
            wikitext="{{Item|name=Teste A}}",
            source_edit_url="https://www.tibiawiki.com.br/index.php?title=Teste_A&action=edit",
            source_raw_url="https://www.tibiawiki.com.br/index.php?title=Teste_A&action=raw",
            source_templates=["Item"],
            fetched_at="2026-03-24T00:00:00+00:00",
            content_hash="hash-a",
            site_profile=profile.key,
        )
        page_b = PageDocument(
            url=url_b,
            slug=slug_b,
            title="Teste B",
            excerpt="Resumo B",
            word_count=90,
            reading_time_minutes=1,
            internal_links=[url_a],
            html_clean="<div><p>Conteudo B</p></div>",
            markdown="Conteudo B",
            fetched_at="2026-03-24T00:00:00+00:00",
            content_hash="hash-b",
            fetch_source="mediawiki_api",
            site_profile=profile.key,
        )

        self.storage.save_page(page_a)
        self.storage.save_page(page_b)
        self.storage.finalize(
            {
                "pages_saved": 2,
                "pages_attempted": 3,
                "source_pages_captured": 1,
                "started_at": "2026-03-24T00:00:00+00:00",
                "finished_at": "2026-03-24T00:01:00+00:00",
            },
            failed_pages={"https://www.tibiawiki.com.br/wiki/Falha": "http_429"},
            site_profile=profile,
            run_config={
                "max_pages": 25,
                "capture_wiki_source": True,
                "respect_robots_txt": True,
            },
        )

        manifest = json.loads((self.tempdir / "data/indexes/pages_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["quickwiki_version"], QUICKWIKI_VERSION)
        self.assertEqual(len(manifest["pages"]), 2)

        summary = json.loads((self.tempdir / "data/indexes/summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["schema_version"], 1)
        self.assertEqual(summary["quickwiki_version"], QUICKWIKI_VERSION)

        html_a = (self.tempdir / self.storage.pages_manifest[slug_a]["paths"]["html"]).read_text(encoding="utf-8")
        self.assertIn("Links desta pagina", html_a)
        self.assertIn("Paginas que apontam para ca", html_a)
        self.assertIn("Links externos", html_a)
        self.assertIn("Codigo-fonte da wiki", html_a)
        self.assertIn("Ver texto-fonte na wiki", html_a)
        self.assertIn("Teste B", html_a)
        self.assertIn("example.com/a", html_a)
        self.assertTrue((self.tempdir / self.storage.pages_manifest[slug_a]["paths"]["source"]).exists())

        diagnostics = json.loads((self.tempdir / "data/indexes/profile_diagnostics.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostics["schema_version"], 1)
        self.assertEqual(diagnostics["quickwiki_version"], QUICKWIKI_VERSION)
        self.assertEqual(diagnostics["profile"]["schema_version"], 1)
        self.assertEqual(diagnostics["profile"]["wiki_family"], "mediawiki")
        self.assertEqual(diagnostics["profile"]["key"], "tibiawiki_br")
        self.assertIn("title_selectors", diagnostics["selectors"])
        self.assertEqual(diagnostics["files"]["run_report"], "data/indexes/run_report.json")

        report = json.loads((self.tempdir / "data/indexes/run_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["quickwiki_version"], QUICKWIKI_VERSION)
        self.assertEqual(report["site_profile"]["key"], "tibiawiki_br")
        self.assertEqual(report["health"]["status"], "warning")
        self.assertEqual(report["failed_pages"]["count"], 1)
        self.assertEqual(report["artifacts"]["admin_page"], "admin/index.html")

        failed_payload = json.loads((self.tempdir / "data/indexes/failed_pages.json").read_text(encoding="utf-8"))
        self.assertEqual(failed_payload["schema_version"], 1)
        self.assertEqual(failed_payload["quickwiki_version"], QUICKWIKI_VERSION)
        self.assertEqual(failed_payload["count"], 1)

        page_json = json.loads(
            (self.tempdir / self.storage.pages_manifest[slug_a]["paths"]["json"]).read_text(encoding="utf-8")
        )
        self.assertEqual(page_json["schema_version"], 1)
        self.assertEqual(page_json["quickwiki_version"], QUICKWIKI_VERSION)

        reloaded_storage = StorageManager(self.tempdir)
        self.assertEqual(set(reloaded_storage.pages_manifest), {slug_a, slug_b})

        admin_html = (self.tempdir / "admin/index.html").read_text(encoding="utf-8")
        self.assertIn("Visao tecnica do espelho", admin_html)
        self.assertIn("Perfil em uso", admin_html)
        self.assertIn("Diagnostico do perfil", admin_html)
        self.assertIn("Detalhes da execucao", admin_html)


if __name__ == "__main__":
    unittest.main()
