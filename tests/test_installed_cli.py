from __future__ import annotations

import os
import subprocess
import sysconfig
import tempfile
import unittest
from pathlib import Path


class InstalledCliSmokeTests(unittest.TestCase):
    def test_installed_cli_lists_profiles_outside_repo(self) -> None:
        script_name = "quickwiki.exe" if os.name == "nt" else "quickwiki"
        script_path = Path(sysconfig.get_path("scripts")) / script_name
        if not script_path.exists():
            self.skipTest("Installed quickwiki entrypoint not found in the active environment.")

        with tempfile.TemporaryDirectory() as tempdir:
            result = subprocess.run(
                [os.fspath(script_path), "--list-site-profiles"],
                cwd=tempdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        self.assertEqual(result.returncode, 0, msg=output)
        self.assertIn("tibiawiki_br", output)
        self.assertIn("tibia_fandom", output)

    def test_installed_cli_ignores_unrelated_profiles_directory_in_cwd(self) -> None:
        script_name = "quickwiki.exe" if os.name == "nt" else "quickwiki"
        script_path = Path(sysconfig.get_path("scripts")) / script_name
        if not script_path.exists():
            self.skipTest("Installed quickwiki entrypoint not found in the active environment.")

        with tempfile.TemporaryDirectory() as tempdir:
            (Path(tempdir) / "profiles").mkdir()
            result = subprocess.run(
                [os.fspath(script_path), "--list-site-profiles"],
                cwd=tempdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        self.assertEqual(result.returncode, 0, msg=output)
        self.assertIn("tibiawiki_br", output)
        self.assertIn("tibia_fandom", output)


if __name__ == "__main__":
    unittest.main()
