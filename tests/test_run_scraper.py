from __future__ import annotations

import asyncio
import io
import logging
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from run_scraper import async_main, configure_logging, main, parse_args
from scraper.presentation import build_console_formatter, build_file_formatter, quickwiki_supports_color
from scraper.version import QUICKWIKI_VERSION


class RunScraperCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parent.parent
        self.previous_cwd = Path.cwd()
        os.chdir(self.project_root)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            handler.close()

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
        self.assertIn("Perfis oficiais desta versao", help_text)
        self.assertIn("tibiawiki_br", help_text)
        self.assertIn("caso avancado", help_text.lower())

    def test_version_flag_prints_public_product_version(self) -> None:
        stdout = io.StringIO()

        with self.assertRaises(SystemExit) as result:
            with redirect_stdout(stdout):
                parse_args(["--version"])

        self.assertEqual(result.exception.code, 0)
        self.assertIn(QUICKWIKI_VERSION, stdout.getvalue())

    def test_main_returns_controlled_error_for_invalid_seed_url(self) -> None:
        for site_profile in ("tibiawiki_br", "auto"):
            stderr = io.StringIO()

            with self.subTest(site_profile=site_profile):
                with redirect_stderr(stderr):
                    exit_code = main(
                        [
                            "--site-profile",
                            site_profile,
                            "--seed-url",
                            "https://example.com/wiki/Foo",
                            "--max-pages",
                            "1",
                            "--fresh",
                        ]
                    )

                self.assertEqual(exit_code, 2)
                self.assertIn("O link inicial nao pertence ao dominio permitido", stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())
                stderr.seek(0)
                stderr.truncate(0)

    def test_main_serve_only_missing_output_fails_without_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            missing_output_dir = Path(tempdir) / "missing-output"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(["--serve-only", "--output-dir", os.fspath(missing_output_dir)])

            self.assertEqual(exit_code, 2)
            self.assertFalse(missing_output_dir.exists())
            self.assertIn("Pasta de sa", stderr.getvalue())

    def test_read_only_profile_commands_do_not_create_output_dir(self) -> None:
        for command_flag in ("--list-site-profiles", "--validate-site-profiles"):
            with self.subTest(command_flag=command_flag):
                with tempfile.TemporaryDirectory() as tempdir:
                    output_dir = Path(tempdir) / "output"
                    args = parse_args([command_flag, "--output-dir", os.fspath(output_dir)])

                    exit_code = asyncio.run(async_main(args))

                    self.assertEqual(exit_code, 0)
                    self.assertFalse(output_dir.exists())

    def test_configure_logging_closes_previous_handlers(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            first_output_dir = Path(tempdir) / "first"
            second_output_dir = Path(tempdir) / "second"
            configure_logging(first_output_dir, "INFO")
            first_file_handler = next(
                handler for handler in logging.getLogger().handlers if isinstance(handler, logging.FileHandler)
            )

            configure_logging(second_output_dir, "INFO")
            root = logging.getLogger()
            for handler in root.handlers[:]:
                root.removeHandler(handler)
                handler.close()

        self.assertTrue(first_file_handler.stream is None or first_file_handler.stream.closed)

    def test_console_formatter_uses_color_when_forced(self) -> None:
        class TtyBuffer(io.StringIO):
            def isatty(self) -> bool:
                return True

        stream = TtyBuffer()
        with patch.dict(os.environ, {"QUICKWIKI_COLOR": "always"}, clear=False):
            formatter = build_console_formatter(stream)
            record = logging.LogRecord(
                "quickwiki.scraper",
                logging.INFO,
                __file__,
                0,
                "Espelho iniciado",
                (),
                None,
            )
            output = formatter.format(record)

        self.assertTrue(quickwiki_supports_color(stream))
        self.assertIn("\x1b[", output)
        self.assertIn("Espelho iniciado", output)

    def test_console_formatter_disables_color_with_no_color(self) -> None:
        class TtyBuffer(io.StringIO):
            def isatty(self) -> bool:
                return True

        stream = TtyBuffer()
        with patch.dict(os.environ, {"NO_COLOR": "1"}, clear=True):
            formatter = build_console_formatter(stream)
            record = logging.LogRecord(
                "quickwiki.scraper",
                logging.WARNING,
                __file__,
                0,
                "Atenção",
                (),
                None,
            )
            output = formatter.format(record)
            color_supported = quickwiki_supports_color(stream)

        self.assertFalse(color_supported)
        self.assertNotIn("\x1b[", output)

    def test_file_formatter_never_writes_ansi_sequences(self) -> None:
        formatter = build_file_formatter()
        record = logging.LogRecord(
            "quickwiki.scraper",
            logging.ERROR,
            __file__,
            0,
            "\x1b[31mFalha\x1b[0m",
            (),
            None,
        )

        output = formatter.format(record)

        self.assertIn("quickwiki.scraper", output)
        self.assertIn("Falha", output)
        self.assertNotIn("\x1b[", output)


if __name__ == "__main__":
    unittest.main()
