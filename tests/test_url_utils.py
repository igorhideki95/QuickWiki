from __future__ import annotations

import unittest

from scraper.config import ScraperConfig
from scraper.url_utils import canonicalize_url


class UrlUtilsTests(unittest.TestCase):
    def test_canonicalize_mediawiki_index_url(self) -> None:
        result = canonicalize_url(
            "/w/index.php?title=Dragon_Lord&action=edit",
            "https://www.tibiawiki.com.br/wiki/Home",
            allowed_domains=("www.tibiawiki.com.br", "tibiawiki.com.br"),
        )
        self.assertEqual(result, "https://www.tibiawiki.com.br/wiki/Dragon_Lord")

    def test_canonicalize_rejects_irrelevant_query_variants(self) -> None:
        result = canonicalize_url(
            "/wiki/Dragon_Lord?foo=bar",
            "https://www.tibiawiki.com.br/wiki/Home",
            allowed_domains=("www.tibiawiki.com.br", "tibiawiki.com.br"),
        )
        self.assertIsNone(result)

    def test_config_bootstrap_auto_only_for_full_crawl(self) -> None:
        self.assertTrue(ScraperConfig(max_pages=None, api_bootstrap_mode="auto").should_bootstrap_from_api())
        self.assertFalse(ScraperConfig(max_pages=20, api_bootstrap_mode="auto").should_bootstrap_from_api())
        self.assertTrue(ScraperConfig(max_pages=20, api_bootstrap_mode="always").should_bootstrap_from_api())


if __name__ == "__main__":
    unittest.main()
