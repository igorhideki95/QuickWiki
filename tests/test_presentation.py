from __future__ import annotations

import unittest

from scraper.presentation import (
    build_gui_exception_payload,
    humanize_fetch_source_label,
    humanize_public_key,
)


class PresentationTests(unittest.TestCase):
    def test_build_gui_exception_payload_uses_public_shape(self) -> None:
        payload = build_gui_exception_payload(ValueError("Perfil nao encontrado nesta interface: custom"))

        self.assertIn("message", payload)
        self.assertIn("level", payload)
        self.assertEqual(payload["level"], "error")
        self.assertIn("hint", payload)

    def test_humanize_fetch_source_label_maps_public_terms(self) -> None:
        self.assertEqual(humanize_fetch_source_label("mediawiki_api"), "API da wiki")
        self.assertEqual(humanize_fetch_source_label("direct_http"), "Pagina web")

    def test_humanize_public_key_maps_public_labels(self) -> None:
        self.assertEqual(humanize_public_key("run_report"), "Detalhes da execucao")
        self.assertEqual(humanize_public_key("runtime_status"), "Status da execucao")


if __name__ == "__main__":
    unittest.main()
