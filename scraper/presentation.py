from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, TextIO


ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
ANSI_RESET = "\033[0m"
LEVEL_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[38;5;81m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[41m\033[97m",
}


@dataclass(slots=True, frozen=True)
class PublicFeedback:
    message: str
    hint: str = ""
    details: str = ""
    level: str = "info"

    def to_payload(self) -> dict[str, str]:
        payload = {
            "message": self.message,
            "level": self.level,
        }
        if self.hint:
            payload["hint"] = self.hint
        if self.details:
            payload["details"] = self.details
        return payload


def build_feedback_payload(
    message: str,
    *,
    hint: str = "",
    details: str = "",
    level: str = "info",
) -> dict[str, str]:
    payload = PublicFeedback(message=message, hint=hint, details=details, level=level).to_payload()
    payload["error"] = message
    return payload


def build_public_error_payload(
    exc: Exception,
    *,
    fallback_message: str = "Nao foi possivel concluir essa acao agora.",
) -> dict[str, str]:
    raw_details = strip_ansi(str(exc).strip())
    if not raw_details:
        return build_feedback_payload(
            fallback_message,
            hint="Tente novamente. Se o problema continuar, revise os logs do QuickWiki.",
            level="error",
        )

    normalized = raw_details.lower()
    message = raw_details
    hint = ""
    details = ""

    if "execucao em andamento" in normalized:
        hint = "Pare a execucao atual antes de iniciar outro espelho."
    elif "nenhuma execucao ativa" in normalized:
        hint = "Inicie um espelho primeiro para depois pedir a parada."
    elif "perfil desconhecido" in normalized or "perfil nao encontrado" in normalized:
        hint = "Escolha um dos perfis listados na tela e tente novamente."
    elif "json invalido" in normalized:
        hint = "Atualize a pagina e tente novamente."
    elif "nivel de detalhe" in normalized or ("log" in normalized and "nivel" in normalized):
        hint = "Escolha INFO, DEBUG, WARNING ou ERROR."
    elif "descoberta inicial" in normalized or "bootstrap" in normalized:
        hint = "Use uma das opcoes de descoberta inicial disponiveis na tela."
    elif "pasta de saida" in normalized:
        hint = "Confira o caminho informado e tente de novo."
    elif "dominio permitido" in normalized:
        hint = "Revise o link inicial ou troque o perfil selecionado."
    elif "nao foi possivel" in normalized:
        hint = "Confira os campos e tente novamente."
    else:
        message = fallback_message
        details = raw_details
        hint = "Tente novamente. Se o problema continuar, revise os logs do QuickWiki."

    return build_feedback_payload(message, hint=hint, details=details, level="error")


def build_gui_exception_payload(exc: Exception) -> dict[str, str]:
    return build_public_error_payload(
        exc,
        fallback_message="Nao foi possivel concluir esta acao agora.",
    )


def strip_ansi(value: str) -> str:
    return ANSI_PATTERN.sub("", value)


def quickwiki_supports_color(stream: TextIO) -> bool:
    mode = os.environ.get("QUICKWIKI_COLOR", "auto").strip().lower() or "auto"
    if os.environ.get("NO_COLOR"):
        return False
    if mode == "never":
        return False
    if mode == "always":
        return True
    is_tty = getattr(stream, "isatty", None)
    return bool(callable(is_tty) and is_tty())


class QuickWikiConsoleFormatter(logging.Formatter):
    def __init__(self, *, use_color: bool) -> None:
        super().__init__(datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname.upper()
        level_text = level.ljust(7)
        message = record.getMessage()
        channel = getattr(record, "quickwiki_channel", "")

        if self.use_color:
            color = LEVEL_COLORS.get(level, "")
            level_display = f"{color}{level_text}{ANSI_RESET}" if color else level_text
        else:
            level_display = level_text

        parts = [timestamp, level_display]
        if channel:
            parts.append(str(channel))
        line = " | ".join(parts) + f" | {message}"

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


def build_console_formatter(stream: TextIO) -> QuickWikiConsoleFormatter:
    return QuickWikiConsoleFormatter(use_color=quickwiki_supports_color(stream))


class QuickWikiFileFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        clone = logging.makeLogRecord(record.__dict__.copy())
        clone.msg = strip_ansi(record.getMessage())
        clone.args = ()
        formatted = super().format(clone)
        return strip_ansi(formatted)


def build_file_formatter() -> logging.Formatter:
    return QuickWikiFileFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def format_studio_log(message: str, *, level: str = "INFO", channel: str = "Studio") -> str:
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"{timestamp} | {level.upper()} | {channel} | {message}"


def humanize_health_label(value: str) -> str:
    mapping = {
        "ok": "Tudo certo",
        "warning": "Atencao",
        "error": "Precisa de revisao",
    }
    normalized = value.strip().lower()
    return mapping.get(normalized, value.strip().title())


def humanize_health(value: str) -> str:
    return humanize_health_label(value)


def humanize_phase_label(value: str) -> str:
    mapping = {
        "starting": "Preparando",
        "bootstrapping": "Descoberta inicial",
        "crawling": "Copiando paginas",
        "retrying": "Tentando novamente",
        "finalizing": "Organizando a saida",
        "completed": "Concluido",
        "failed": "Interrompido",
        "idle": "Parado",
    }
    normalized = value.strip().lower()
    return mapping.get(normalized, value.strip().title())


def humanize_fetch_source_label(value: str) -> str:
    mapping = {
        "direct_http": "Pagina web",
        "mediawiki_api": "API da wiki",
        "unknown": "Origem nao informada",
    }
    normalized = value.strip().lower()
    return mapping.get(normalized, value.strip().replace("_", " ").title())


def humanize_public_key(value: str) -> str:
    mapping = {
        "summary": "Resumo",
        "run_report": "Detalhes da execucao",
        "profile_diagnostics": "Perfil carregado",
        "manifest": "Lista de paginas",
        "search_index": "Busca interna",
        "runtime_status": "Status da execucao",
        "admin_page": "Area tecnica",
        "landing_page": "Pagina inicial",
        "pages_saved": "Paginas salvas",
        "assets_saved": "Arquivos salvos",
        "categories_indexed": "Categorias",
        "duplicate_content_groups": "Conteudos parecidos",
        "failed_pages": "Paginas com falha",
        "pages_attempted": "Paginas tentadas",
        "links_discovered": "Links encontrados",
        "source_pages_captured": "Paginas com codigo-fonte",
        "failure_rate": "Taxa de falhas",
        "source_capture_rate": "Cobertura do codigo-fonte",
        "retry_recovery_rate": "Recuperacao nas novas tentativas",
        "title_selectors": "Titulos",
        "content_root_selectors": "Bloco principal",
        "category_selectors": "Categorias",
        "extra_noise_selectors": "Elementos para limpar",
    }
    normalized = value.strip()
    return mapping.get(normalized, normalized.replace("_", " ").title())


def first_health_note(health: dict[str, Any]) -> str:
    notes = health.get("notes", []) if isinstance(health.get("notes"), list) else []
    warnings = health.get("warnings", []) if isinstance(health.get("warnings"), list) else []
    for item in [*warnings, *notes]:
        text = str(item).strip()
        if text:
            return text
    return ""
