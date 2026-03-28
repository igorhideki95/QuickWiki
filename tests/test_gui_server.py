from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scraper.gui_server import (
    QuickWikiGuiApp,
    build_missing_project_docs_page,
    build_scraper_subprocess_command,
    normalize_gui_run_request,
    resolve_gui_project_doc,
    safe_path_join,
)
from scraper.version import QUICKWIKI_VERSION


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
        self.assertEqual(command[:3], ["python", "-m", "quickwiki"])
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
            docs_dir = project_root / "docs"
            docs_dir.mkdir()
            (docs_dir / "ARTIFACT_CONTRACTS.md").write_text("contracts", encoding="utf-8")
            (docs_dir / "PROFILE_SCHEMA.md").write_text("profile schema", encoding="utf-8")
            (docs_dir / "RELEASE_CHECKLIST.md").write_text("checklist", encoding="utf-8")
            hidden_dir = project_root / ".git"
            hidden_dir.mkdir()
            (hidden_dir / "config").write_text("secret", encoding="utf-8")

            readme = resolve_gui_project_doc(project_root, "readme")
            contracts = resolve_gui_project_doc(project_root, "artifact-contracts")
            profile_schema = resolve_gui_project_doc(project_root, "profile-schema")
            hidden = resolve_gui_project_doc(project_root, ".git/config")
            missing = resolve_gui_project_doc(project_root, "notes")

        self.assertEqual(readme, (project_root / "README.md").resolve())
        self.assertEqual(contracts, (project_root / "docs" / "ARTIFACT_CONTRACTS.md").resolve())
        self.assertEqual(profile_schema, (project_root / "docs" / "PROFILE_SCHEMA.md").resolve())
        self.assertIsNone(hidden)
        self.assertIsNone(missing)

    def test_gui_app_state_exposes_profiles_with_default_seed(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = QuickWikiGuiApp(project_root)

        state = app.state_payload()
        tibiawiki_profile = next(profile for profile in state["profiles"] if profile["key"] == "tibiawiki_br")

        self.assertEqual(state["product"]["version"], QUICKWIKI_VERSION)
        self.assertEqual(state["product"]["canonical_entrypoint"], "quickwiki")
        self.assertEqual(state["product"]["module_entrypoint"], "python -m quickwiki")
        self.assertIn("tibiawiki_br", state["product"]["supported_profile_keys"])
        self.assertEqual(tibiawiki_profile["schema_version"], 1)
        self.assertEqual(tibiawiki_profile["wiki_family"], "mediawiki")
        self.assertEqual(state["defaults"]["output_dir"], str((project_root / "output").resolve()))
        self.assertIn("default_seed_url", tibiawiki_profile)
        self.assertTrue(tibiawiki_profile["default_seed_url"].startswith("https://"))

    def test_gui_app_state_exposes_runtime_and_report_payloads(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = QuickWikiGuiApp(project_root)

        with tempfile.TemporaryDirectory() as tempdir:
            output_dir = Path(tempdir)
            runtime_path = output_dir / "checkpoints" / "runtime_status.json"
            report_path = output_dir / "data" / "indexes" / "run_report.json"
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(
                json.dumps({"phase": "crawling", "queue": {"pending": 7}}, ensure_ascii=False),
                encoding="utf-8",
            )
            report_path.write_text(
                json.dumps({"health": {"status": "warning"}}, ensure_ascii=False),
                encoding="utf-8",
            )

            app.active_output_dir = output_dir
            state = app.state_payload()

        self.assertEqual(state["runtime"]["phase"], "crawling")
        self.assertEqual(state["runtime"]["queue"]["pending"], 7)
        self.assertEqual(state["report"]["health"]["status"], "warning")
        self.assertEqual(state["links"]["report"], "/mirror/data/indexes/run_report.json")

    def test_gui_app_hides_manual_link_when_manual_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            project_root = Path(tempdir)
            profiles_dir = Path(__file__).resolve().parent.parent / "scraper" / "bundled" / "profiles"
            app = QuickWikiGuiApp(project_root, profiles_dir=profiles_dir, docs_root=None, manual_root=None)

            state = app.state_payload()

        self.assertEqual(state["links"]["manual"], "")

    def test_missing_project_docs_page_mentions_quickwiki_root(self) -> None:
        page = build_missing_project_docs_page("documentacao do projeto")

        self.assertIn("QUICKWIKI_ROOT", page)
        self.assertIn("documentacao do projeto", page)


if __name__ == "__main__":
    unittest.main()
