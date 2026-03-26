from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path

from scraper.models import PageDocument
from scraper.site_profiles import resolve_site_profile
from scraper.storage import StorageManager


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path.cwd() / ".test-artifacts"
        root.mkdir(parents=True, exist_ok=True)
        self.tempdir = root / f"quickwiki-tests-{uuid.uuid4().hex}"
        self.tempdir.mkdir(parents=True, exist_ok=True)
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
            html_clean="<div><p>Conteúdo A</p></div>",
            markdown="Conteúdo A",
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
            html_clean="<div><p>Conteúdo B</p></div>",
            markdown="Conteúdo B",
            fetched_at="2026-03-24T00:00:00+00:00",
            content_hash="hash-b",
            fetch_source="mediawiki_api",
            site_profile=profile.key,
        )

        self.storage.save_page(page_a)
        self.storage.save_page(page_b)
        self.storage.finalize({"pages_saved": 2}, failed_pages={}, site_profile=profile)

        manifest = json.loads((self.tempdir / "data/indexes/pages_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), 2)

        html_a = (self.tempdir / self.storage.pages_manifest[slug_a]["paths"]["html"]).read_text(encoding="utf-8")
        self.assertIn("Links internos", html_a)
        self.assertIn("Backlinks", html_a)
        self.assertIn("Links externos", html_a)
        self.assertIn("Código-fonte wiki", html_a)
        self.assertIn("Ver código fonte", html_a)
        self.assertIn("Teste B", html_a)
        self.assertIn("example.com/a", html_a)
        self.assertTrue((self.tempdir / self.storage.pages_manifest[slug_a]["paths"]["source"]).exists())

        diagnostics = json.loads((self.tempdir / "data/indexes/profile_diagnostics.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostics["profile"]["key"], "tibiawiki_br")
        self.assertIn("title_selectors", diagnostics["selectors"])

        admin_html = (self.tempdir / "admin/index.html").read_text(encoding="utf-8")
        self.assertIn("QuickWiki Admin", admin_html)
        self.assertIn("Painel do perfil ativo", admin_html)
        self.assertIn("JSON do perfil", admin_html)


if __name__ == "__main__":
    unittest.main()
