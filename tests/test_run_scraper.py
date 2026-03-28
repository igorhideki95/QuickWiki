from __future__ import annotations

import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from run_scraper import parse_args
from scraper.version import QUICKWIKI_VERSION


class RunScraperCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parent.parent
        self.previous_cwd = Path.cwd()
        os.chdir(self.project_root)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)

    def test_parse_args_defaults_to_repo_paths(self) -> None:
        args = parse_args([])

        self.assertEqual(args.output_dir, self.project_root / "output")
        self.assertEqual(args.profiles_dir, self.project_root / "profiles")
        self.assertEqual(args.site_profile, "auto")

    def test_parse_args_uses_bundled_profiles_when_workspace_is_not_repo_root(self) -> None:
        outside_root = self.project_root / ".test-artifacts" / "parse-args-workspace"
        bundled_profiles_dir = self.project_root / "scraper" / "bundled" / "profiles"

        with patch("run_scraper.resolve_project_root", return_value=outside_root), patch(
            "run_scraper.resolve_profiles_dir",
            return_value=bundled_profiles_dir,
        ):
            args = parse_args([])

        self.assertEqual(args.output_dir, outside_root / "output")
        self.assertEqual(args.profiles_dir, bundled_profiles_dir)

    def test_help_mentions_public_support_boundary(self) -> None:
        stdout = io.StringIO()

        with self.assertRaises(SystemExit) as result:
            with redirect_stdout(stdout):
                parse_args(["--help"])

        help_text = stdout.getvalue()
        self.assertEqual(result.exception.code, 0)
        self.assertIn("Perfis oficialmente suportados no v1", help_text)
        self.assertIn("tibiawiki_br", help_text)
        self.assertIn("preview", help_text.lower())

    def test_version_flag_prints_public_product_version(self) -> None:
        stdout = io.StringIO()

        with self.assertRaises(SystemExit) as result:
            with redirect_stdout(stdout):
                parse_args(["--version"])

        self.assertEqual(result.exception.code, 0)
        self.assertIn(QUICKWIKI_VERSION, stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
