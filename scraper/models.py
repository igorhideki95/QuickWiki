from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ImageRecord:
    original_url: str
    thumbnail_url: str
    alt: str
    title: str
    context_text: str
    local_asset_path: str | None = None
    sha256: str | None = None
    bucket: str = "images"


@dataclass(slots=True)
class PageDocument:
    url: str
    slug: str
    title: str
    excerpt: str = ""
    word_count: int = 0
    reading_time_minutes: int = 0
    headings: list[dict[str, Any]] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    lists: list[list[str]] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)
    code_blocks: list[str] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    infoboxes: list[dict[str, Any]] = field(default_factory=list)
    templates: list[dict[str, Any]] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    images: list[ImageRecord] = field(default_factory=list)
    html_clean: str = ""
    markdown: str = ""
    wikitext: str = ""
    source_edit_url: str = ""
    source_raw_url: str = ""
    source_templates: list[str] = field(default_factory=list)
    fetched_at: str = ""
    content_hash: str = ""
    source_encoding: str | None = None
    fetch_source: str = "direct_http"
    site_profile: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["images"] = [asdict(image) for image in self.images]
        return payload
