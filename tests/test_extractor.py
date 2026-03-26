from __future__ import annotations

import unittest

from scraper.extractor import PageExtractor
from scraper.site_profiles import resolve_site_profile


class ExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = PageExtractor(resolve_site_profile("tibiawiki_br", None))

    def test_extract_page_generates_excerpt_and_rewrites_links(self) -> None:
        html = """
        <html>
          <body>
            <h1 id="firstHeading">Arena PvP</h1>
            <div id="mw-content-text">
              <div class="mw-parser-output">
                <!-- hidden -->
                <h2><span class="mw-headline">Resumo</span></h2>
                <p>As arenas PvP eram zonas especiais usadas para treinar combate sem perdas reais.</p>
                <a href="/wiki/Thais">Thais</a>
                <a href="https://example.com/wiki">Externo</a>
              </div>
            </div>
          </body>
        </html>
        """

        page = self.extractor.extract_page(
            url="https://www.tibiawiki.com.br/wiki/Arena_PvP",
            slug="Arena_PvP--slug",
            html=html,
            source_encoding="utf-8",
            internal_link_resolver=lambda slug: f"local/{slug}.html",
        )

        self.assertEqual(page.title, "Arena PvP")
        self.assertIn("zonas especiais", page.excerpt)
        self.assertGreater(page.word_count, 5)
        self.assertEqual(page.reading_time_minutes, 1)
        self.assertIn("https://www.tibiawiki.com.br/wiki/Thais", page.internal_links)
        self.assertIn("https://example.com/wiki", page.external_links)
        self.assertNotIn("hidden", page.html_clean)
        self.assertIn('href="local/Thais--', page.html_clean)


if __name__ == "__main__":
    unittest.main()
