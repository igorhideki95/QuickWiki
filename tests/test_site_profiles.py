from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scraper.paths import resolve_profiles_dir
from scraper.site_profiles import load_site_profiles, resolve_site_profile, validate_site_profile_payload


class SiteProfilesTests(unittest.TestCase):
    def test_builtin_profiles_expose_schema_version_and_family(self) -> None:
        profiles = load_site_profiles()

        self.assertEqual(profiles["tibiawiki_br"].schema_version, 1)
        self.assertEqual(profiles["tibiawiki_br"].wiki_family, "mediawiki")
        self.assertEqual(profiles["tibia_fandom"].schema_version, 1)
        self.assertEqual(profiles["tibia_fandom"].wiki_family, "fandom")

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

    def test_validate_site_profile_payload_rejects_unknown_schema_version(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema_version"):
            validate_site_profile_payload(
                {
                    "schema_version": 99,
                    "wiki_family": "mediawiki",
                    "key": "future_profile",
                    "default_seed_url": "https://example.com/wiki/Home",
                    "allowed_domains": ["example.com"],
                },
                definition_path="memory://future-profile",
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

            with self.assertRaisesRegex(ValueError, "Perfil inv"):
                load_site_profiles(Path(tempdir))

    def test_load_site_profiles_defaults_legacy_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            profile_path = Path(tempdir) / "legacy.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "key": "legacy_profile",
                        "default_seed_url": "https://example.com/wiki/Home",
                        "allowed_domains": ["example.com"],
                    }
                ),
                encoding="utf-8",
            )

            profiles = load_site_profiles(Path(tempdir))

        self.assertEqual(profiles["legacy_profile"].schema_version, 1)
        self.assertEqual(profiles["legacy_profile"].wiki_family, "mediawiki")

    def test_load_site_profiles_rejects_malformed_json_profile_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            profile_path = Path(tempdir) / "broken.json"
            profile_path.write_text('{"key": "broken"', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON malformado"):
                load_site_profiles(Path(tempdir))

    def test_resolve_profiles_dir_uses_bundled_profiles_when_source_root_is_unavailable(self) -> None:
        with patch("scraper.paths.find_source_project_root", return_value=None):
            bundled_dir = resolve_profiles_dir()

        self.assertTrue((bundled_dir / "tibiawiki_br.json").exists())
        self.assertTrue((bundled_dir / "tibia_fandom.json").exists())

    def test_load_site_profiles_missing_directory_explains_source_first_model(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            missing_dir = Path(tempdir) / "missing"

            with self.assertRaisesRegex(FileNotFoundError, "QUICKWIKI_ROOT"):
                load_site_profiles(missing_dir)


if __name__ == "__main__":
    unittest.main()
