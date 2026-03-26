from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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
