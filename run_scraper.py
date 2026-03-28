from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Sequence

from scraper.paths import find_source_project_root, resolve_profiles_dir, resolve_project_root
from scraper.presentation import build_console_formatter, build_file_formatter
from scraper.site_profiles import load_site_profiles, resolve_site_profile
from scraper.url_utils import canonicalize_url
from scraper.version import QUICKWIKI_VERSION, SUPPORTED_BUILTIN_SITE_PROFILES

LOGGER_NAME = "quickwiki.scraper"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = resolve_project_root()
    default_profiles_dir = resolve_profiles_dir()
    parser = argparse.ArgumentParser(
        description="QuickWiki cria copias offline navegaveis de wikis MediaWiki e Fandom para leitura, busca e auditoria local.",
        epilog=(
            "Perfis oficiais desta versao: "
            + ", ".join(SUPPORTED_BUILTIN_SITE_PROFILES)
            + ". Voce ainda pode carregar perfis externos pela CLI quando precisar de um caso avancado."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {QUICKWIKI_VERSION}")
    parser.add_argument(
        "--seed-url",
        default=None,
        help="Link inicial do espelho. Se voce nao informar nada, o QuickWiki usa a pagina inicial do perfil escolhido.",
    )
    parser.add_argument(
        "--site-profile",
        default="auto",
        help="Perfil da wiki. Use 'auto' para detectar pelo dominio ou escolha um perfil como tibiawiki_br.",
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        default=default_profiles_dir,
        help="Pasta com perfis de wiki em JSON.",
    )
    parser.add_argument(
        "--site-profile-file",
        type=Path,
        action="append",
        default=[],
        help="Arquivo JSON extra de perfil para carregar junto com a pasta de perfis.",
    )
    parser.add_argument(
        "--list-site-profiles",
        action="store_true",
        help="Mostra os perfis disponiveis e encerra.",
    )
    parser.add_argument(
        "--validate-site-profiles",
        action="store_true",
        help="Confere se os perfis carregados estao validos e encerra.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "output",
        help="Pasta onde o espelho offline sera salvo.",
    )
    parser.add_argument("--workers", type=int, default=8, help="Quantidade de paginas processadas em paralelo.")
    parser.add_argument(
        "--asset-workers",
        type=int,
        default=8,
        help="Quantidade maxima de downloads de imagens e outros arquivos por pagina.",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=2.0,
        help="Ritmo maximo de requisicoes por segundo.",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="Tempo limite de cada requisicao, em segundos.")
    parser.add_argument("--max-retries", type=int, default=4, help="Numero maximo de tentativas por requisicao.")
    parser.add_argument(
        "--retry-failed-passes",
        type=int,
        default=1,
        help="Quantas novas tentativas fazer para paginas que falharem.",
    )
    parser.add_argument(
        "--no-source",
        action="store_true",
        help="Nao salvar o codigo-fonte da wiki quando ele estiver disponivel.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=25,
        help="Salvar um checkpoint a cada N paginas concluidas.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limite opcional de paginas para um teste pequeno ou uma execucao parcial.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignora checkpoints antigos e comeca um espelho novo.",
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Ignora o robots.txt. Use apenas quando voce souber o impacto.",
    )
    parser.add_argument(
        "--api-bootstrap-mode",
        default="auto",
        choices=["auto", "always", "off"],
        help="Controla a descoberta inicial por API para ampliar a cobertura do espelho.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Depois do espelho, abre um servidor local para navegar pelos arquivos.",
    )
    parser.add_argument(
        "--serve-only",
        action="store_true",
        help="Abre o espelho ja existente sem rodar um novo crawl.",
    )
    parser.add_argument(
        "--serve-port",
        type=int,
        default=8765,
        help="Porta do servidor local usada com --serve ou --serve-only.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Abre a interface local do QuickWiki Studio.",
    )
    parser.add_argument(
        "--gui-port",
        type=int,
        default=8877,
        help="Porta da interface local quando --gui for usado.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de detalhe mostrado no terminal.",
    )
    return parser.parse_args(argv)


def configure_logging(output_dir: Path | None, level_name: str, *, stream: Any | None = None) -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    stream_target = stream if stream is not None else sys.stderr
    stream_handler = logging.StreamHandler(stream_target)
    stream_handler.setFormatter(build_console_formatter(stream_handler.stream))
    root.addHandler(stream_handler)

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        logs_dir = output_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        logfile = logs_dir / "scraper.log"
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setFormatter(build_file_formatter())
        root.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


async def async_main(args: argparse.Namespace) -> int:
    from scraper.config import ScraperConfig
    from scraper.crawler import QuickWikiCrawler

    output_dir = args.output_dir.expanduser().resolve()
    extra_profile_files = tuple(path.expanduser().resolve() for path in args.site_profile_file)
    logger = logging.getLogger(LOGGER_NAME)

    if args.list_site_profiles or args.validate_site_profiles:
        configure_logging(None, args.log_level)
        try:
            profiles = load_site_profiles(args.profiles_dir, extra_profile_files=extra_profile_files)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            logger.error("%s", exc)
            return 2
        for key in sorted(profiles):
            profile = profiles[key]
            logger.info("Perfil pronto: %s | %s | pagina inicial %s", profile.key, profile.label, profile.default_seed_url)
        if args.validate_site_profiles:
            logger.info("Validacao concluida: %s perfil(is) pronto(s) para uso.", len(profiles))
        return 0

    if args.serve_only:
        return 0

    configure_logging(output_dir, args.log_level)

    try:
        profile = resolve_site_profile(
            args.site_profile,
            args.seed_url,
            profiles_dir=args.profiles_dir.expanduser().resolve(),
            extra_profile_files=extra_profile_files,
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        logger.error("%s", exc)
        return 2

    seed_url = args.seed_url or profile.default_seed_url
    canonical_seed_url = canonicalize_url(
        seed_url,
        seed_url,
        allowed_domains=profile.allowed_domains,
        allowed_prefix=profile.allowed_path_prefix,
    )
    if canonical_seed_url is None:
        logger.error("O link inicial nao pertence ao dominio permitido: %s", seed_url)
        return 2

    config = ScraperConfig(
        seed_url=canonical_seed_url,
        site_profile=profile.key,
        profiles_dir=args.profiles_dir.expanduser().resolve(),
        site_profile_files=extra_profile_files,
        output_dir=output_dir,
        workers=max(1, args.workers),
        asset_workers_per_page=max(1, args.asset_workers),
        rate_limit_per_sec=max(0.1, args.rate_limit),
        timeout_seconds=max(3.0, args.timeout),
        max_retries=max(0, args.max_retries),
        retry_failed_passes=max(0, args.retry_failed_passes),
        capture_wiki_source=not args.no_source,
        checkpoint_every_pages=max(1, args.checkpoint_every),
        max_pages=args.max_pages,
        resume=not args.fresh,
        respect_robots_txt=not args.ignore_robots,
        api_bootstrap_mode=args.api_bootstrap_mode,
    )

    crawler = QuickWikiCrawler(config)
    stats = await crawler.run()

    logging.getLogger(LOGGER_NAME).info(
        "Espelho concluido: perfil %s | %s paginas | %s arquivos | %ss",
        profile.label,
        stats.get("pages_saved"),
        stats.get("assets_downloaded"),
        stats.get("duration_seconds"),
    )
    return 0


def serve_output(output_dir: Path, port: int) -> int:
    output_dir = output_dir.expanduser().resolve()
    if not output_dir.exists():
        raise FileNotFoundError(f"Pasta de saida nao encontrada: {output_dir}")

    handler = lambda *handler_args, **handler_kwargs: SimpleHTTPRequestHandler(  # noqa: E731
        *handler_args,
        directory=os.fspath(output_dir),
        **handler_kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Espelho disponivel em http://127.0.0.1:%s/index.html", port)
    logger.info("Use Ctrl+C para encerrar o servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor local encerrado pelo usuario.")
    finally:
        server.server_close()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    extra_profile_files = tuple(path.expanduser().resolve() for path in args.site_profile_file)
    if args.gui:
        from scraper.gui_server import run_quickwiki_gui

        source_project_root = find_source_project_root()
        configure_logging(args.output_dir.expanduser().resolve(), args.log_level)
        return run_quickwiki_gui(
            resolve_project_root(),
            args.gui_port,
            profiles_dir=args.profiles_dir.expanduser().resolve(),
            site_profile_files=extra_profile_files,
            docs_root=source_project_root,
            manual_root=(source_project_root / "Manual do Usu\u00e1rio") if source_project_root else None,
        )
    if args.serve_only:
        configure_logging(None, args.log_level)
        try:
            return serve_output(args.output_dir, args.serve_port)
        except FileNotFoundError as exc:
            logging.getLogger(LOGGER_NAME).error("%s", exc)
            return 2

    exit_code = asyncio.run(async_main(args))
    if exit_code != 0:
        return exit_code

    if args.serve:
        return serve_output(args.output_dir, args.serve_port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
