from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .site_profiles import WikiSiteProfile
from .version import build_artifact_metadata, build_product_payload


def summarize_failed_pages(
    failed_pages: dict[str, str],
    *,
    sample_size: int = 8,
) -> dict[str, Any]:
    ordered_items = sorted((str(url), str(reason)) for url, reason in failed_pages.items())
    reasons = Counter(reason for _, reason in ordered_items)
    return {
        "count": len(ordered_items),
        "reasons": [
            {"reason": reason, "count": count}
            for reason, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0]))
        ],
        "samples": [
            {"url": url, "reason": reason}
            for url, reason in ordered_items[:sample_size]
        ],
    }


def build_health_payload(
    *,
    stats: dict[str, Any],
    failed_summary: dict[str, Any],
    run_config: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    pending_count: int | None = None,
) -> dict[str, Any]:
    config = run_config or {}
    summary_payload = summary or {}

    pages_attempted = int(stats.get("pages_attempted", 0) or 0)
    pages_saved = int(summary_payload.get("pages_saved", stats.get("pages_saved", 0)) or 0)
    failed_count = int(failed_summary.get("count", 0) or 0)
    source_pages_captured = int(stats.get("source_pages_captured", 0) or 0)
    pages_retried = int(stats.get("pages_retried", 0) or 0)
    failed_pages_recovered = int(stats.get("failed_pages_recovered", 0) or 0)

    failure_rate = round((failed_count / pages_attempted), 4) if pages_attempted else 0.0
    source_capture_rate = round((source_pages_captured / pages_saved), 4) if pages_saved else 0.0
    recovery_rate = round((failed_pages_recovered / pages_retried), 4) if pages_retried else 0.0

    warnings: list[str] = []
    notes: list[str] = []
    status = "ok"

    if pages_attempted and pages_saved == 0:
        status = "error"
        warnings.append("Nenhuma pagina foi salva; revise seed URL, perfil e seletores.")
    elif failed_count and failure_rate >= 0.3:
        status = "warning"
        warnings.append(f"Taxa de falha elevada ({failed_count}/{pages_attempted}).")
    elif failed_count:
        status = "warning"
        warnings.append(f"Foram registradas {failed_count} pagina(s) com falha.")

    max_pages = config.get("max_pages")
    if max_pages is not None:
        notes.append(f"Execucao parcial configurada com max_pages={max_pages}.")

    if config.get("capture_wiki_source") and pages_saved and source_capture_rate == 0.0:
        notes.append("Nenhuma pagina capturou source wiki nesta execucao.")

    if config.get("respect_robots_txt") is False:
        notes.append("robots.txt foi ignorado nesta execucao.")

    if pending_count:
        notes.append(f"{pending_count} URL(s) seguem pendente(s) no frontier.")

    retry_rounds = int(stats.get("retry_rounds_completed", 0) or 0)
    if retry_rounds:
        notes.append(f"{retry_rounds} rodada(s) de retry executada(s).")

    return {
        "status": status,
        "warnings": warnings,
        "notes": notes,
        "metrics": {
            "failure_rate": failure_rate,
            "source_capture_rate": source_capture_rate,
            "retry_recovery_rate": recovery_rate,
        },
    }


def build_runtime_status(
    *,
    phase: str,
    stats: dict[str, Any],
    failed_pages: dict[str, str],
    visited_count: int,
    enqueued_count: int,
    pending_count: int,
    site_profile: WikiSiteProfile | None,
    run_config: dict[str, Any] | None,
) -> dict[str, Any]:
    generated_at = datetime.now(UTC).isoformat()
    failed_summary = summarize_failed_pages(failed_pages)
    return {
        **build_artifact_metadata("runtime_status", generated_at=generated_at),
        "updated_at": generated_at,
        "phase": phase,
        "running": phase not in {"completed", "failed", "idle"},
        "product": build_product_payload(),
        "site_profile": _site_profile_payload(site_profile),
        "run_config": dict(run_config or {}),
        "stats": dict(stats),
        "queue": {
            "visited": visited_count,
            "enqueued": enqueued_count,
            "pending": pending_count,
        },
        "failed_pages": failed_summary,
        "health": build_health_payload(
            stats=stats,
            failed_summary=failed_summary,
            run_config=run_config,
            pending_count=pending_count,
        ),
    }


def build_run_report(
    *,
    output_root: Path,
    summary: dict[str, Any],
    stats: dict[str, Any],
    failed_pages: dict[str, str],
    site_profile: WikiSiteProfile | None,
    run_config: dict[str, Any] | None,
) -> dict[str, Any]:
    generated_at = datetime.now(UTC).isoformat()
    failed_summary = summarize_failed_pages(failed_pages)
    return {
        **build_artifact_metadata("run_report", generated_at=generated_at),
        "output_root": str(output_root.resolve()),
        "product": build_product_payload(),
        "site_profile": _site_profile_payload(site_profile),
        "run_config": dict(run_config or {}),
        "summary": {
            "generated_at": summary.get("generated_at", ""),
            "pages_saved": summary.get("pages_saved", 0),
            "assets_saved": summary.get("assets_saved", 0),
            "categories_indexed": summary.get("categories_indexed", 0),
            "duplicate_content_groups": summary.get("duplicate_content_groups", 0),
            "failed_pages": summary.get("failed_pages", 0),
            "fetch_sources": dict(summary.get("fetch_sources", {})),
        },
        "stats": dict(stats),
        "failed_pages": failed_summary,
        "health": build_health_payload(
            stats=stats,
            failed_summary=failed_summary,
            run_config=run_config,
            summary=summary,
        ),
        "artifacts": {
            "landing_page": "index.html",
            "admin_page": "admin/index.html",
            "summary_json": "data/indexes/summary.json",
            "run_report_json": "data/indexes/run_report.json",
            "failed_pages_json": "data/indexes/failed_pages.json",
            "pages_manifest_json": "data/indexes/pages_manifest.json",
            "profile_diagnostics_json": "data/indexes/profile_diagnostics.json",
            "search_index_js": "data/indexes/search_index.js",
            "checkpoint_json": "checkpoints/state.json",
            "runtime_status_json": "checkpoints/runtime_status.json",
            "log_file": "logs/scraper.log",
        },
    }


def _site_profile_payload(site_profile: WikiSiteProfile | None) -> dict[str, Any]:
    if site_profile is None:
        return {
            "key": "",
            "label": "",
            "description": "",
            "definition_path": "",
        }
    return {
        "key": site_profile.key,
        "label": site_profile.label,
        "description": site_profile.description,
        "definition_path": site_profile.definition_path,
    }
