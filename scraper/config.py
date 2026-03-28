from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ScraperConfig:
    seed_url: str = "https://www.tibiawiki.com.br/wiki/Home"
    site_profile: str = "auto"
    profiles_dir: Path | None = None
    site_profile_files: tuple[Path, ...] = ()
    output_dir: Path = field(default_factory=lambda: Path("output"))
    user_agent: str = "QuickWikiBot/1.0 (+offline mirror for personal research)"

    workers: int = 8
    rate_limit_per_sec: float = 2.0
    timeout_seconds: float = 30.0
    max_retries: int = 4
    backoff_base_seconds: float = 1.2
    checkpoint_every_pages: int = 25
    max_pages: int | None = None
    asset_workers_per_page: int = 8
    retry_failed_passes: int = 1
    capture_wiki_source: bool = True

    resume: bool = True
    respect_robots_txt: bool = True
    api_bootstrap_mode: str = "auto"

    allowed_domains: tuple[str, ...] = ("www.tibiawiki.com.br", "tibiawiki.com.br")
    allowed_path_prefix: str = "/wiki/"

    def normalized_output_dir(self) -> Path:
        return self.output_dir.expanduser().resolve()

    def should_bootstrap_from_api(self) -> bool:
        mode = self.api_bootstrap_mode.lower().strip()
        if mode == "always":
            return True
        if mode == "off":
            return False
        return self.max_pages is None

    def to_runtime_dict(self) -> dict[str, Any]:
        return {
            "seed_url": self.seed_url,
            "site_profile": self.site_profile,
            "profiles_dir": str(self.profiles_dir) if self.profiles_dir else "",
            "site_profile_files": [str(path) for path in self.site_profile_files],
            "output_dir": str(self.normalized_output_dir()),
            "user_agent": self.user_agent,
            "workers": self.workers,
            "asset_workers_per_page": self.asset_workers_per_page,
            "rate_limit_per_sec": self.rate_limit_per_sec,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "backoff_base_seconds": self.backoff_base_seconds,
            "checkpoint_every_pages": self.checkpoint_every_pages,
            "max_pages": self.max_pages,
            "retry_failed_passes": self.retry_failed_passes,
            "capture_wiki_source": self.capture_wiki_source,
            "resume": self.resume,
            "respect_robots_txt": self.respect_robots_txt,
            "api_bootstrap_mode": self.api_bootstrap_mode,
            "allowed_domains": list(self.allowed_domains),
            "allowed_path_prefix": self.allowed_path_prefix,
        }
