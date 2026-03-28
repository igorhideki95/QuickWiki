"""QuickWiki offline mirror scraper package."""

from .config import ScraperConfig
from .crawler import QuickWikiCrawler, TibiaWikiCrawler
from .gui_server import run_quickwiki_gui
from .version import QUICKWIKI_VERSION as __version__
from .site_profiles import (
    available_site_profile_keys,
    load_site_profiles,
    resolve_site_profile,
    validate_site_profile_payload,
)

__all__ = [
    "QuickWikiCrawler",
    "ScraperConfig",
    "TibiaWikiCrawler",
    "__version__",
    "available_site_profile_keys",
    "load_site_profiles",
    "resolve_site_profile",
    "run_quickwiki_gui",
    "validate_site_profile_payload",
]
