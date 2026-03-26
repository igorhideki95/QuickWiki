from __future__ import annotations

import unittest

from scraper.crawler import _extract_template_names_from_wikitext


class CrawlerSourceTests(unittest.TestCase):
    def test_extract_template_names_from_wikitext(self) -> None:
        wikitext = """
        {{Item
        |name=Amber Sabre
        }}
        {{Infobox Creature|name=Dragon}}
        {{subst:SomeTemplate}}
        """
        self.assertEqual(
            _extract_template_names_from_wikitext(wikitext)[:3],
            ["Item", "Infobox Creature", "SomeTemplate"],
        )


if __name__ == "__main__":
    unittest.main()
