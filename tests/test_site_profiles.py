from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scraper.site_profiles import load_site_profiles, resolve_site_profile, validate_site_profile_payload


class SiteProfilesTests(unittest.TestCase):
    def test_auto_detects_tibiawiki_br(self) -> None:
        profile = resolve_site_profile("auto", "https://www.tibiawiki.com.br/wiki/Home")
        self.assertEqual(profile.key, "tibiawiki_br")

    def test_auto_detects_tibia_fandom(self) -> None:
        profile = resolve_site_profile("auto", "https://tibia.fandom.com/wiki/TibiaWiki")
        self.assertEqual(profile.key, "tibia_fandom")

    def test_profile_builds_source_urls(self) -> None:
        profiles = load_site_profiles()
        edit_url, raw_url = profiles["tibia_fandom"].build_source_urls("Amber Sabre")
        self.assertIn("title=Amber_Sabre", edit_url)
        self.assertTrue(edit_url.endswith("&action=edit"))
        self.assertTrue(raw_url.endswith("&action=raw"))

    def test_validate_site_profile_payload_rejects_seed_outside_allowed_domains(self) -> None:
        with self.assertRaisesRegex(ValueError, "default_seed_url"):
            validate_site_profile_payload(
                {
                    "key": "quickwiki_invalid",
                    "default_seed_url": "https://example.com/wiki/Home",
                    "allowed_domains": ["another.example.com"],
                },
                definition_path="memory://invalid-profile",
            )

    def test_load_site_profiles_rejects_invalid_profile_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            profile_path = Path(tempdir) / "invalid.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "key": "QuickWiki Invalid",
                        "default_seed_url": "https://example.com/wiki/Home",
                        "allowed_domains": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Perfil inválido"):
                load_site_profiles(Path(tempdir))


if __name__ == "__main__":
    unittest.main()
