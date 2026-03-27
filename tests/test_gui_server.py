from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scraper.gui_server import (
    QuickWikiGuiApp,
    build_scraper_subprocess_command,
    normalize_gui_run_request,
    resolve_gui_project_doc,
    safe_path_join,
)


class GuiServerTests(unittest.TestCase):
    def test_normalize_gui_run_request_applies_defaults_and_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            project_root = Path(tempdir)
            request = normalize_gui_run_request(
                {
                    "site_profile": "TIBIA_FANDOM",
                    "output_dir": "output-gui",
                    "workers": "0",
                    "asset_workers": "",
                    "rate_limit": "0",
                    "timeout": "1",
                    "max_retries": "-2",
                    "retry_failed_passes": "-1",
                    "checkpoint_every": "0",
                    "api_bootstrap_mode": "always",
                    "log_level": "debug",
                    "fresh": "true",
                    "ignore_robots": "yes",
                    "no_source": "false",
                },
                project_root,
            )

        self.assertEqual(request.site_profile, "tibia_fandom")
        self.assertEqual(request.output_dir, (project_root / "output-gui").resolve())
        self.assertEqual(request.workers, 1)
        self.assertEqual(request.asset_workers, 8)
        self.assertEqual(request.rate_limit, 0.1)
        self.assertEqual(request.timeout, 3.0)
        self.assertEqual(request.max_retries, 0)
        self.assertEqual(request.retry_failed_passes, 0)
        self.assertEqual(request.checkpoint_every, 1)
        self.assertEqual(request.api_bootstrap_mode, "always")
        self.assertEqual(request.log_level, "DEBUG")
        self.assertTrue(request.fresh)
        self.assertTrue(request.ignore_robots)
        self.assertFalse(request.no_source)

    def test_normalize_gui_run_request_rejects_invalid_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            project_root = Path(tempdir)
            with self.assertRaisesRegex(ValueError, "bootstrap"):
                normalize_gui_run_request({"api_bootstrap_mode": "bad"}, project_root)
            with self.assertRaisesRegex(ValueError, "log"):
                normalize_gui_run_request({"log_level": "TRACE"}, project_root)

    def test_build_scraper_subprocess_command_contains_selected_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            project_root = Path(tempdir)
            request = normalize_gui_run_request(
                {
                    "site_profile": "tibiawiki_br",
                    "seed_url": "https://www.tibiawiki.com.br/wiki/Home",
                    "output_dir": "mirror-output",
                    "max_pages": "12",
                    "fresh": True,
                    "ignore_robots": True,
                    "no_source": True,
                },
                project_root,
            )

        command = build_scraper_subprocess_command(request, python_executable="python")
        self.assertEqual(command[:2], ["python", "run_scraper.py"])
        self.assertIn("--site-profile", command)
        self.assertIn("tibiawiki_br", command)
        self.assertIn("--seed-url", command)
        self.assertIn("--max-pages", command)
        self.assertIn("--fresh", command)
        self.assertIn("--ignore-robots", command)
        self.assertIn("--no-source", command)
        self.assertIn(str((project_root / "mirror-output").resolve()), command)

    def test_safe_path_join_blocks_directory_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            base_dir = Path(tempdir)
            nested_file = base_dir / "docs" / "index.html"
            nested_file.parent.mkdir(parents=True, exist_ok=True)
            nested_file.write_text("ok", encoding="utf-8")

            safe = safe_path_join(base_dir, "docs/index.html")
            blocked = safe_path_join(base_dir, "../outside.txt")

        self.assertEqual(safe, nested_file.resolve())
        self.assertIsNone(blocked)

    def test_resolve_gui_project_doc_allows_only_known_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            project_root = Path(tempdir)
            (project_root / "README.md").write_text("readme", encoding="utf-8")
            (project_root / "CHANGELOG.md").write_text("changes", encoding="utf-8")
            (project_root / "DOCUMENTACAO_TECNICA.md").write_text("docs", encoding="utf-8")
            hidden_dir = project_root / ".git"
            hidden_dir.mkdir()
            (hidden_dir / "config").write_text("secret", encoding="utf-8")

            readme = resolve_gui_project_doc(project_root, "readme")
            hidden = resolve_gui_project_doc(project_root, ".git/config")
            missing = resolve_gui_project_doc(project_root, "notes")

        self.assertEqual(readme, (project_root / "README.md").resolve())
        self.assertIsNone(hidden)
        self.assertIsNone(missing)

    def test_gui_app_state_exposes_profiles_with_default_seed(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = QuickWikiGuiApp(project_root)

        state = app.state_payload()
        tibiawiki_profile = next(profile for profile in state["profiles"] if profile["key"] == "tibiawiki_br")

        self.assertEqual(state["defaults"]["output_dir"], str((project_root / "output").resolve()))
        self.assertIn("default_seed_url", tibiawiki_profile)
        self.assertTrue(tibiawiki_profile["default_seed_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
