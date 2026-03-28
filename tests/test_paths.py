from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scraper.paths import _is_source_project_root, resolve_project_root


class PathsTests(unittest.TestCase):
    def test_resolve_project_root_falls_back_to_cwd_outside_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            expected_root = Path(tempdir).resolve()
            with patch("scraper.paths.find_source_project_root", return_value=None), patch(
                "scraper.paths.Path.cwd",
                return_value=expected_root,
            ):
                resolved = resolve_project_root()

        self.assertEqual(resolved, expected_root)

    def test_is_source_project_root_requires_profiles_and_run_scraper(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            candidate = Path(tempdir)
            (candidate / "profiles").mkdir()
            self.assertFalse(_is_source_project_root(candidate))

            (candidate / "run_scraper.py").write_text("print('ok')", encoding="utf-8")
            self.assertTrue(_is_source_project_root(candidate))


if __name__ == "__main__":
    unittest.main()
