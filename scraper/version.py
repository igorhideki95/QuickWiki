from __future__ import annotations

from typing import Any


QUICKWIKI_VERSION = "1.0.0"

SUPPORTED_BUILTIN_SITE_PROFILES = (
    "tibiawiki_br",
    "tibia_fandom",
)

EXTERNAL_PROFILE_SUPPORT_MODE = "preview"

PUBLIC_ARTIFACT_SCHEMA_VERSIONS = {
    "page_document": 1,
    "pages_manifest": 1,
    "summary": 1,
    "failed_pages": 1,
    "profile_diagnostics": 1,
    "run_report": 1,
    "runtime_status": 1,
}


def build_product_payload() -> dict[str, Any]:
    return {
        "name": "QuickWiki",
        "version": QUICKWIKI_VERSION,
        "distribution_model": "source-first",
        "canonical_entrypoint": "quickwiki",
        "module_entrypoint": "python -m quickwiki",
        "compatibility_entrypoint": "python run_scraper.py",
        "source_root_env_var": "QUICKWIKI_ROOT",
        "supported_profile_keys": list(SUPPORTED_BUILTIN_SITE_PROFILES),
        "external_profiles_mode": EXTERNAL_PROFILE_SUPPORT_MODE,
        "primary_operator_platform": "Windows",
        "secondary_operator_platform": "Linux (source install)",
    }


def build_artifact_metadata(
    artifact_name: str,
    *,
    generated_at: str = "",
) -> dict[str, Any]:
    payload = {
        "schema_version": PUBLIC_ARTIFACT_SCHEMA_VERSIONS[artifact_name],
        "quickwiki_version": QUICKWIKI_VERSION,
    }
    if generated_at:
        payload["generated_at"] = generated_at
    return payload
