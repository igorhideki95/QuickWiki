from __future__ import annotations

import json
import logging
import mimetypes
import os
import shlex
import subprocess
import sys
import threading
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .gui_assets import GUI_CSS, GUI_INDEX_HTML, GUI_JS
from .site_profiles import WikiSiteProfile, load_site_profiles
from .version import build_product_payload


LOGGER_NAME = "quickwiki.scraper"
VALID_API_BOOTSTRAP_MODES = frozenset({"auto", "always", "off"})
VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})
GUI_PROJECT_DOCS = {
    "readme": Path("README.md"),
    "changelog": Path("CHANGELOG.md"),
    "technical-docs": Path("DOCUMENTACAO_TECNICA.md"),
    "artifact-contracts": Path("docs") / "ARTIFACT_CONTRACTS.md",
    "profile-schema": Path("docs") / "PROFILE_SCHEMA.md",
    "release-checklist": Path("docs") / "RELEASE_CHECKLIST.md",
}


@dataclass(slots=True)
class GuiRunRequest:
    site_profile: str
    seed_url: str | None
    output_dir: Path
    workers: int
    asset_workers: int
    rate_limit: float
    timeout: float
    max_retries: int
    retry_failed_passes: int
    checkpoint_every: int
    max_pages: int | None
    api_bootstrap_mode: str
    log_level: str
    fresh: bool
    ignore_robots: bool
    no_source: bool


def normalize_gui_run_request(payload: dict[str, Any], project_root: Path) -> GuiRunRequest:
    def clean_text(value: Any, default: str = "") -> str:
        if value is None:
            return default
        return str(value).strip()

    def clean_int(value: Any, default: int, minimum: int | None = None) -> int:
        candidate = default if value in {"", None} else int(value)
        if minimum is not None:
            candidate = max(minimum, candidate)
        return candidate

    def clean_float(value: Any, default: float, minimum: float | None = None) -> float:
        candidate = default if value in {"", None} else float(value)
        if minimum is not None:
            candidate = max(minimum, candidate)
        return candidate

    def clean_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "sim"}
        return False

    seed_url = clean_text(payload.get("seed_url")) or None
    output_dir_value = clean_text(payload.get("output_dir"), "output")
    output_dir = Path(output_dir_value).expanduser()
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()

    max_pages_raw = clean_text(payload.get("max_pages"))
    max_pages = clean_int(max_pages_raw, 25, minimum=1) if max_pages_raw else None

    api_bootstrap_mode = clean_text(payload.get("api_bootstrap_mode"), "auto").lower() or "auto"
    if api_bootstrap_mode not in VALID_API_BOOTSTRAP_MODES:
        raise ValueError("Modo de bootstrap API invalido.")

    log_level = clean_text(payload.get("log_level"), "INFO").upper() or "INFO"
    if log_level not in VALID_LOG_LEVELS:
        raise ValueError("Nivel de log invalido.")

    return GuiRunRequest(
        site_profile=clean_text(payload.get("site_profile"), "auto").lower() or "auto",
        seed_url=seed_url,
        output_dir=output_dir,
        workers=clean_int(payload.get("workers"), 8, minimum=1),
        asset_workers=clean_int(payload.get("asset_workers"), 8, minimum=1),
        rate_limit=clean_float(payload.get("rate_limit"), 2.0, minimum=0.1),
        timeout=clean_float(payload.get("timeout"), 30.0, minimum=3.0),
        max_retries=clean_int(payload.get("max_retries"), 4, minimum=0),
        retry_failed_passes=clean_int(payload.get("retry_failed_passes"), 1, minimum=0),
        checkpoint_every=clean_int(payload.get("checkpoint_every"), 25, minimum=1),
        max_pages=max_pages,
        api_bootstrap_mode=api_bootstrap_mode,
        log_level=log_level,
        fresh=clean_bool(payload.get("fresh")),
        ignore_robots=clean_bool(payload.get("ignore_robots")),
        no_source=clean_bool(payload.get("no_source")),
    )


def build_scraper_subprocess_command(
    request: GuiRunRequest,
    *,
    python_executable: str | None = None,
) -> list[str]:
    command = [python_executable or sys.executable, "-m", "quickwiki"]
    command.extend(["--site-profile", request.site_profile])
    command.extend(["--output-dir", str(request.output_dir)])
    command.extend(["--workers", str(request.workers)])
    command.extend(["--asset-workers", str(request.asset_workers)])
    command.extend(["--rate-limit", str(request.rate_limit)])
    command.extend(["--timeout", str(request.timeout)])
    command.extend(["--max-retries", str(request.max_retries)])
    command.extend(["--retry-failed-passes", str(request.retry_failed_passes)])
    command.extend(["--checkpoint-every", str(request.checkpoint_every)])
    command.extend(["--api-bootstrap-mode", request.api_bootstrap_mode])
    command.extend(["--log-level", request.log_level])

    if request.seed_url:
        command.extend(["--seed-url", request.seed_url])
    if request.max_pages is not None:
        command.extend(["--max-pages", str(request.max_pages)])
    if request.fresh:
        command.append("--fresh")
    if request.ignore_robots:
        command.append("--ignore-robots")
    if request.no_source:
        command.append("--no-source")

    return command


def format_command_preview(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def is_textual_content_type(content_type: str) -> bool:
    return content_type.startswith("text/") or content_type in {
        "application/javascript",
        "application/json",
        "application/xml",
        "image/svg+xml",
    }


class QuickWikiGuiApp:
    def __init__(
        self,
        project_root: Path,
        *,
        profiles_dir: Path | None = None,
        docs_root: Path | None = None,
        manual_root: Path | None = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.profiles_dir = (profiles_dir or (self.project_root / "profiles")).resolve()
        default_docs_root = self.project_root if (self.project_root / "README.md").exists() else None
        default_manual_root = self.project_root / "Manual do Usuário"
        self.docs_root = docs_root.resolve() if docs_root is not None else default_docs_root
        self.manual_root = (
            manual_root.resolve()
            if manual_root is not None
            else default_manual_root.resolve() if default_manual_root.exists() else None
        )
        self.logger = logging.getLogger(LOGGER_NAME)
        self.lock = threading.Lock()
        self.process: subprocess.Popen[str] | None = None
        self.started_at: str | None = None
        self.finished_at: str | None = None
        self.last_exit_code: int | None = None
        self.command_preview: str = ""
        self.logs: deque[str] = deque(maxlen=400)
        self.active_output_dir = (project_root / "output").resolve()
        self.site_profiles: dict[str, WikiSiteProfile] = {}
        self.refresh_profiles()

    def refresh_profiles(self) -> dict[str, WikiSiteProfile]:
        profiles = load_site_profiles(self.profiles_dir)
        self.site_profiles = profiles
        return profiles

    def state_payload(self) -> dict[str, Any]:
        with self.lock:
            process = self.process
            running = process is not None and process.poll() is None
            run_state = {
                "running": running,
                "pid": process.pid if running else None,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "last_exit_code": self.last_exit_code,
                "command_preview": self.command_preview,
            }
            log_lines = list(self.logs)
            output_dir = self.active_output_dir

        if not log_lines:
            log_lines = self._tail_log_file(output_dir)

        return {
            "product": build_product_payload(),
            "profiles": self._profiles_payload(),
            "defaults": {
                "seed_url": "",
                "output_dir": str(output_dir),
            },
            "run": run_state,
            "summary": self._load_summary(output_dir),
            "runtime": self._load_runtime_status(output_dir),
            "report": self._load_run_report(output_dir),
            "logs": log_lines,
            "links": {
                "mirror": "/mirror/index.html",
                "admin": "/mirror/admin/index.html",
                "summary": "/mirror/data/indexes/summary.json",
                "report": "/mirror/data/indexes/run_report.json",
                "runtime": "/mirror/checkpoints/runtime_status.json",
                "manual": "/manual/index.html" if self.manual_root and self.manual_root.exists() else "",
            },
        }

    def validate_profiles(self) -> dict[str, Any]:
        profiles = self.refresh_profiles()
        return {
            "message": f"{len(profiles)} perfil(is) validado(s) com sucesso.",
            "profiles": self._profiles_payload(),
        }

    def start_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = normalize_gui_run_request(payload, self.project_root)
        profiles = self.refresh_profiles()
        self._ensure_profile_choice(request.site_profile, profiles)

        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise RuntimeError("Ja existe uma execucao em andamento.")

            command = build_scraper_subprocess_command(request)
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            process = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
            )
            self.process = process
            self.started_at = datetime.now(UTC).isoformat()
            self.finished_at = None
            self.last_exit_code = None
            self.command_preview = format_command_preview(command)
            self.logs.clear()
            self.logs.append(f"[studio] Execucao iniciada em {self.started_at}")
            self.logs.append(f"[studio] Comando: {self.command_preview}")
            self.logs.append(f"[studio] Saida ativa: {request.output_dir}")
            self.active_output_dir = request.output_dir

        threading.Thread(target=self._pump_process_output, args=(process,), daemon=True).start()
        return {"message": "Execucao iniciada com sucesso."}

    def stop_run(self) -> dict[str, Any]:
        with self.lock:
            process = self.process
            if process is None or process.poll() is not None:
                raise RuntimeError("Nenhuma execucao ativa para encerrar.")
            self.logs.append("[studio] Enviando sinal de encerramento para o processo...")

        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        return {"message": "Execucao encerrada pela GUI."}

    def _pump_process_output(self, process: subprocess.Popen[str]) -> None:
        if process.stdout is not None:
            for line in process.stdout:
                text = line.rstrip()
                if not text:
                    continue
                with self.lock:
                    self.logs.append(text)

        exit_code = process.wait()
        finished_at = datetime.now(UTC).isoformat()
        with self.lock:
            self.finished_at = finished_at
            self.last_exit_code = exit_code
            if self.process is process:
                self.process = None
            self.logs.append(f"[studio] Execucao finalizada em {finished_at} com exit code {exit_code}.")

    def _profiles_payload(self) -> list[dict[str, Any]]:
        payload = [
            {
                "key": "auto",
                "label": "Auto detectar",
                "description": "Detecta o perfil ideal a partir do dominio da seed URL.",
                "default_seed_url": "",
                "schema_version": 0,
                "wiki_family": "auto",
            }
        ]
        for key in sorted(self.site_profiles):
            profile = self.site_profiles[key]
            payload.append(
                {
                    "key": profile.key,
                    "label": profile.label,
                    "description": profile.description,
                    "default_seed_url": profile.default_seed_url,
                    "schema_version": profile.schema_version,
                    "wiki_family": profile.wiki_family,
                }
            )
        return payload

    def _ensure_profile_choice(
        self,
        site_profile: str,
        profiles: dict[str, WikiSiteProfile] | None = None,
    ) -> None:
        if site_profile == "auto":
            return
        active_profiles = profiles or self.site_profiles
        if site_profile not in active_profiles:
            raise ValueError(f"Perfil desconhecido para a GUI: {site_profile}")

    def _load_summary(self, output_dir: Path) -> dict[str, Any]:
        return self._load_json_file(output_dir / "data" / "indexes" / "summary.json")

    def _load_runtime_status(self, output_dir: Path) -> dict[str, Any]:
        return self._load_json_file(output_dir / "checkpoints" / "runtime_status.json")

    def _load_run_report(self, output_dir: Path) -> dict[str, Any]:
        return self._load_json_file(output_dir / "data" / "indexes" / "run_report.json")

    def _tail_log_file(self, output_dir: Path) -> list[str]:
        log_path = output_dir / "logs" / "scraper.log"
        if not log_path.exists():
            return []
        try:
            lines = log_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
        return lines[-80:]

    def _load_json_file(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}


class QuickWikiGuiHandler(BaseHTTPRequestHandler):
    server: "QuickWikiGuiServer"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path in {"/", "/index.html"}:
            self._send_text(GUI_INDEX_HTML, "text/html; charset=utf-8")
            return
        if path == "/app.css":
            self._send_text(GUI_CSS, "text/css; charset=utf-8")
            return
        if path == "/app.js":
            self._send_text(GUI_JS, "application/javascript; charset=utf-8")
            return
        if path == "/api/state":
            self._send_json(self.server.app.state_payload())
            return
        if path.startswith("/manual/"):
            if self.server.app.manual_root is None:
                self._send_text(build_missing_project_docs_page("manual do usuario"), "text/html; charset=utf-8")
                return
            self._serve_from_dir(self.server.app.manual_root, path.removeprefix("/manual/"))
            return
        if path.startswith("/mirror/"):
            self._serve_from_dir(self.server.app.active_output_dir, path.removeprefix("/mirror/"))
            return
        if path.startswith("/docs/"):
            if self.server.app.docs_root is None:
                self._send_text(
                    build_missing_project_docs_page("documentacao do projeto"),
                    "text/html; charset=utf-8",
                )
                return
            document = resolve_gui_project_doc(self.server.app.docs_root, path.removeprefix("/docs/"))
            if document is None:
                self._send_text(
                    build_missing_project_docs_page("documentacao do projeto"),
                    "text/html; charset=utf-8",
                )
                return
            self._serve_file(document)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Recurso nao encontrado.")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        payload = self._read_json_body()

        try:
            if path == "/api/start-run":
                self._send_json(self.server.app.start_run(payload), status=HTTPStatus.CREATED)
                return
            if path == "/api/validate-profiles":
                self._send_json(self.server.app.validate_profiles())
                return
            if path == "/api/stop-run":
                self._send_json(self.server.app.stop_run())
                return
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint nao encontrado.")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        self.server.app.logger.debug("gui.http | " + format, *args)

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Corpo JSON invalido.") from exc
        return payload if isinstance(payload, dict) else {}

    def _send_json(self, payload: dict[str, Any], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, content: str, content_type: str) -> None:
        body = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_from_dir(self, base_dir: Path, raw_relative_path: str) -> None:
        safe_path = safe_path_join(base_dir, raw_relative_path or "index.html")
        if safe_path is None or not safe_path.exists() or not safe_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado.")
            return
        self._serve_file(safe_path)

    def _serve_file(self, safe_path: Path) -> None:
        content_type, _ = mimetypes.guess_type(safe_path.name)
        final_content_type = content_type or "application/octet-stream"
        if is_textual_content_type(final_content_type):
            final_content_type += "; charset=utf-8"

        body = safe_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", final_content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class QuickWikiGuiServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], app: QuickWikiGuiApp) -> None:
        super().__init__(server_address, QuickWikiGuiHandler)
        self.app = app


def safe_path_join(base_dir: Path, raw_relative_path: str) -> Path | None:
    relative = raw_relative_path.lstrip("/")
    if not relative:
        relative = "index.html"
    candidate = (base_dir / Path(unquote(relative))).resolve()
    base = base_dir.resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


def resolve_gui_project_doc(project_root: Path, doc_key: str) -> Path | None:
    relative_path = GUI_PROJECT_DOCS.get(doc_key.strip().lower())
    if relative_path is None:
        return None

    candidate = (project_root / relative_path).resolve()
    base = project_root.resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None

    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def build_missing_project_docs_page(label: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QuickWiki Studio - Recurso indisponivel</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f7f1e8;
        --panel: rgba(255, 251, 246, 0.96);
        --border: rgba(142, 47, 26, 0.16);
        --accent: #8e2f1a;
        --text: #3f281f;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background:
          radial-gradient(circle at top, rgba(255, 255, 255, 0.82), transparent 44%),
          linear-gradient(160deg, #f5ede1 0%, #f3efe8 48%, #e9f0ed 100%);
        color: var(--text);
        font: 16px/1.6 "Segoe UI", sans-serif;
        padding: 24px;
      }}
      main {{
        max-width: 720px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 18px 50px rgba(115, 80, 61, 0.12);
      }}
      h1 {{
        margin: 0 0 12px;
        color: var(--accent);
        font: 700 clamp(1.8rem, 4vw, 2.6rem)/1.05 Georgia, serif;
      }}
      p {{
        margin: 0 0 12px;
      }}
      code {{
        background: rgba(142, 47, 26, 0.08);
        border-radius: 999px;
        padding: 2px 8px;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Recurso nao empacotado nesta instalacao</h1>
      <p>O atalho para <strong>{label}</strong> depende do checkout completo do repositorio.</p>
      <p>Para abrir esta parte da experiencia do QuickWiki Studio, execute a GUI a partir da raiz do projeto ou defina <code>QUICKWIKI_ROOT</code> para apontar para um checkout valido.</p>
      <p>O crawler, a validacao de perfis built-in e o fluxo principal continuam disponiveis nesta instalacao.</p>
    </main>
  </body>
</html>"""


def run_quickwiki_gui(
    project_root: Path,
    port: int,
    host: str = "127.0.0.1",
    *,
    profiles_dir: Path | None = None,
    docs_root: Path | None = None,
    manual_root: Path | None = None,
) -> int:
    logger = logging.getLogger(LOGGER_NAME)
    app = QuickWikiGuiApp(
        project_root,
        profiles_dir=profiles_dir,
        docs_root=docs_root,
        manual_root=manual_root,
    )
    server = QuickWikiGuiServer((host, port), app)
    logger.info("QuickWiki Studio disponivel em http://%s:%s", host, port)
    logger.info("Abra a interface no navegador e pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("QuickWiki Studio encerrado pelo usuario.")
    finally:
        server.server_close()
    return 0
