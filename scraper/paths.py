from __future__ import annotations

import os
from pathlib import Path


def find_source_project_root() -> Path | None:
    env_root = os.getenv("QUICKWIKI_ROOT", "").strip()
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "profiles").exists():
            return candidate

    package_root = Path(__file__).resolve().parent.parent
    cwd = Path.cwd().resolve()

    for candidate in (cwd, package_root):
        if (candidate / "profiles").exists() and (candidate / "run_scraper.py").exists():
            return candidate

    for candidate in (cwd, package_root):
        if (candidate / "profiles").exists():
            return candidate

    return None


def resolve_project_root() -> Path:
    return find_source_project_root() or Path.cwd().resolve()


def resolve_profiles_dir() -> Path:
    source_root = find_source_project_root()
    if source_root is not None:
        candidate = (source_root / "profiles").resolve()
        if candidate.exists():
            return candidate

    bundled_profiles = Path(__file__).resolve().parent / "bundled" / "profiles"
    return bundled_profiles.resolve()
