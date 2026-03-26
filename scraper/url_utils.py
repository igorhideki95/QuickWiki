from __future__ import annotations

import hashlib
import posixpath
import re
from pathlib import PurePosixPath
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse, urlunparse

IGNORED_QUERY_KEYS = {
    "action",
    "veaction",
    "oldid",
    "diff",
    "printable",
    "curid",
    "uselang",
    "mobileaction",
    "redirect",
    "variant",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
FILE_NAME_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
MULTI_UNDERSCORE = re.compile(r"_+")


def canonicalize_url(
    raw_url: str,
    current_url: str,
    allowed_domains: tuple[str, ...],
    allowed_prefix: str = "/wiki/",
) -> str | None:
    if not raw_url:
        return None

    raw = raw_url.strip()
    if raw.startswith(("#", "mailto:", "javascript:", "data:", "tel:")):
        return None

    absolute = urljoin(current_url, raw)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None

    domain = parsed.netloc.lower()
    if domain.endswith(":443"):
        domain = domain[:-4]
    if domain not in allowed_domains:
        return None

    path = unquote(parsed.path or "/")
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    if path.rstrip("/").lower() == "/w/index.php":
        title = query_params.get("title", [None])[0]
        if not title:
            return None
        path = f"{allowed_prefix.rstrip('/')}/{title.strip().replace(' ', '_')}"
        query_params = {}

    path = _normalize_path(path)
    if not path.startswith(allowed_prefix):
        return None

    if query_params:
        filtered = {
            key: values
            for key, values in query_params.items()
            if key.lower() not in IGNORED_QUERY_KEYS and not key.lower().startswith("utm_")
        }
        if filtered:
            # Query parameters on wiki pages usually represent UI variants; skip to avoid duplicates.
            return None

    normalized = urlunparse(("https", domain, quote(path, safe="/:_-."), "", "", ""))
    return normalized


def make_absolute_url(raw_url: str | None, current_url: str) -> str | None:
    if not raw_url:
        return None
    candidate = raw_url.strip()
    if not candidate or candidate.startswith(("data:", "javascript:", "mailto:", "tel:")):
        return None
    absolute = urljoin(current_url, candidate)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))


def slug_from_url(url: str, allowed_prefix: str = "/wiki/") -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path)

    if path.startswith(allowed_prefix):
        logical = path[len(allowed_prefix) :].strip("/")
    else:
        logical = path.strip("/")

    if not logical:
        logical = "home"

    logical = logical.replace("/", "__").replace(":", "-").replace(" ", "_")
    logical = FILE_NAME_SAFE.sub("_", logical)
    logical = MULTI_UNDERSCORE.sub("_", logical).strip("_")
    if not logical:
        logical = "home"
    if len(logical) > 120:
        logical = logical[:120].rstrip("_")

    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    return f"{logical}--{digest}"


def shard_from_slug(slug: str) -> str:
    return hashlib.sha1(slug.encode("utf-8")).hexdigest()[:2]


def infer_asset_bucket(page_url: str, image_url: str, alt: str, title: str, context: str) -> str:
    corpus = " ".join([page_url, image_url, alt, title, context]).lower()
    if any(token in corpus for token in {"monster", "creature", "boss", "beast"}):
        return "monsters"
    if any(token in corpus for token in {"item", "equip", "weapon", "armour", "armor", "loot"}):
        return "items"
    if any(token in corpus for token in {"map", "area", "region", "city", "island", "location"}):
        return "maps"
    return "images"


def derive_original_image_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    if "/thumb/" not in parsed.path:
        return image_url

    prefix, suffix = parsed.path.split("/thumb/", maxsplit=1)
    segments = [segment for segment in suffix.split("/") if segment]
    if len(segments) < 4:
        return image_url

    original_path = f"{prefix}/{segments[0]}/{segments[1]}/{segments[2]}"
    return urlunparse((parsed.scheme, parsed.netloc, original_path, "", "", ""))


def extension_from_url(url: str) -> str:
    path = PurePosixPath(unquote(urlparse(url).path))
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix
    return ".bin"


def _normalize_path(path: str) -> str:
    cleaned = re.sub(r"/{2,}", "/", path)
    cleaned = posixpath.normpath(cleaned)
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    if cleaned == "/.":
        cleaned = "/"
    return cleaned
