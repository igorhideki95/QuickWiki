from __future__ import annotations

import argparse
import asyncio
import logging
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from scraper import QuickWikiCrawler, ScraperConfig
from scraper.gui_server import run_quickwiki_gui
from scraper.site_profiles import available_site_profile_keys, load_site_profiles, resolve_site_profile

LOGGER_NAME = "quickwiki.scraper"


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="QuickWiki: espelhador offline multi-wiki com crawler BFS e extração estruturada."
    )
    parser.add_argument(
        "--seed-url",
        default=None,
        help="URL inicial para o crawling. Se omitida, usa a seed padrão do perfil escolhido.",
    )
    parser.add_argument(
        "--site-profile",
        default="auto",
        help="Perfil de wiki a usar. Ex.: tibiawiki_br ou tibia_fandom.",
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        default=root / "profiles",
        help="Diretório com perfis declarativos de wiki em JSON.",
    )
    parser.add_argument(
        "--site-profile-file",
        type=Path,
        action="append",
        default=[],
        help="Arquivo JSON extra de perfil para carregar além do diretório padrão.",
    )
    parser.add_argument(
        "--list-site-profiles",
        action="store_true",
        help="Lista os perfis de wiki carregados e encerra.",
    )
    parser.add_argument(
        "--validate-site-profiles",
        action="store_true",
        help="Valida a estrutura dos perfis carregados, lista o resultado e encerra.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "output",
        help="Pasta onde os dados espelhados serão salvos.",
    )
    parser.add_argument("--workers", type=int, default=8, help="Quantidade de workers paralelos.")
    parser.add_argument(
        "--asset-workers",
        type=int,
        default=8,
        help="Quantidade máxima de downloads de assets em paralelo por página.",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=2.0,
        help="Requisições por segundo (global).",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout por requisição (segundos).")
    parser.add_argument("--max-retries", type=int, default=4, help="Máximo de tentativas por requisição.")
    parser.add_argument(
        "--retry-failed-passes",
        type=int,
        default=1,
        help="Quantidade de rodadas extras para reprocessar páginas que falharam.",
    )
    parser.add_argument(
        "--no-source",
        action="store_true",
        help="Desativa a captura do código-fonte wiki (wikitext/action=edit/action=raw).",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=25,
        help="Salvar checkpoint a cada N páginas salvas.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limite opcional de páginas para execução parcial.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignora checkpoint anterior e inicia novo crawl.",
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Não respeitar robots.txt (não recomendado).",
    )
    parser.add_argument(
        "--api-bootstrap-mode",
        default="auto",
        choices=["auto", "always", "off"],
        help="Controla a descoberta inicial via MediaWiki API para ampliar a cobertura do crawl.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Após o crawl, sobe um servidor HTTP local para navegar no espelho offline.",
    )
    parser.add_argument(
        "--serve-only",
        action="store_true",
        help="Não executa crawl; apenas serve a pasta de saída já existente.",
    )
    parser.add_argument(
        "--serve-port",
        type=int,
        default=8765,
        help="Porta do servidor HTTP local quando --serve/--serve-only for usado.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Abre a GUI local do QuickWiki para configurar e acompanhar execuções.",
    )
    parser.add_argument(
        "--gui-port",
        type=int,
        default=8877,
        help="Porta da GUI local quando --gui for usado.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nível de logs no terminal.",
    )
    return parser.parse_args()


def configure_logging(output_dir: Path, level_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = logs_dir / "scraper.log"

    root = logging.getLogger()
    root.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    root.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


async def async_main(args: argparse.Namespace) -> int:
    output_dir = args.output_dir.expanduser().resolve()
    configure_logging(output_dir, args.log_level)

    extra_profile_files = tuple(path.expanduser().resolve() for path in args.site_profile_file)
    logger = logging.getLogger(LOGGER_NAME)

    if args.list_site_profiles or args.validate_site_profiles:
        try:
            profiles = load_site_profiles(args.profiles_dir, extra_profile_files=extra_profile_files)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            logger.error("%s", exc)
            return 2
        for key in available_site_profile_keys(args.profiles_dir, extra_profile_files=extra_profile_files):
            if key == "auto":
                continue
            profile = profiles[key]
            logger.info("Perfil=%s | label=%s | seed=%s", profile.key, profile.label, profile.default_seed_url)
        if args.validate_site_profiles:
            logger.info("Validação concluída com sucesso: %s perfil(is) carregado(s).", len(profiles))
        return 0

    if args.serve_only:
        return 0

    try:
        profile = resolve_site_profile(
            args.site_profile,
            args.seed_url,
            profiles_dir=args.profiles_dir,
            extra_profile_files=extra_profile_files,
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        logger.error("%s", exc)
        return 2
    seed_url = args.seed_url or profile.default_seed_url

    config = ScraperConfig(
        seed_url=seed_url,
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
        "Finalizado. Perfil=%s | páginas salvas=%s | assets novos=%s | duração=%ss",
        profile.label,
        stats.get("pages_saved"),
        stats.get("assets_downloaded"),
        stats.get("duration_seconds"),
    )
    return 0


def serve_output(output_dir: Path, port: int) -> int:
    output_dir = output_dir.expanduser().resolve()
    if not output_dir.exists():
        raise FileNotFoundError(f"Pasta de saída não encontrada: {output_dir}")

    handler = lambda *handler_args, **handler_kwargs: SimpleHTTPRequestHandler(  # noqa: E731
        *handler_args,
        directory=os.fspath(output_dir),
        **handler_kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Servidor offline disponível em http://127.0.0.1:%s/index.html", port)
    logger.info("Pressione Ctrl+C para encerrar o servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário.")
    finally:
        server.server_close()
    return 0


def main() -> int:
    args = parse_args()
    if args.gui:
        configure_logging(args.output_dir.expanduser().resolve(), args.log_level)
        return run_quickwiki_gui(Path(__file__).resolve().parent, args.gui_port)
    exit_code = asyncio.run(async_main(args))
    if exit_code != 0:
        return exit_code

    if args.serve or args.serve_only:
        return serve_output(args.output_dir, args.serve_port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
