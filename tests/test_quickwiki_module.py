from __future__ import annotations

import io
import runpy
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from quickwiki import __version__, main
from scraper.version import QUICKWIKI_VERSION


class QuickWikiModuleTests(unittest.TestCase):
    def test_package_exports_version_and_main(self) -> None:
        self.assertEqual(__version__, QUICKWIKI_VERSION)
        self.assertTrue(callable(main))

    def test_module_entrypoint_supports_version_flag(self) -> None:
        stdout = io.StringIO()

        with self.assertRaises(SystemExit) as result:
            with redirect_stdout(stdout), patch.object(sys, "argv", ["quickwiki", "--version"]):
                runpy.run_module("quickwiki", run_name="__main__")

        self.assertEqual(result.exception.code, 0)
        self.assertIn(QUICKWIKI_VERSION, stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
