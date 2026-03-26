from __future__ import annotations

import hashlib
import math
import re
from datetime import UTC, datetime
from typing import Callable

from bs4 import BeautifulSoup, Comment, Tag
from markdownify import markdownify as html_to_markdown

from .models import ImageRecord, PageDocument
from .site_profiles import WikiSiteProfile
from .url_utils import (
    canonicalize_url,
    derive_original_image_url,
    make_absolute_url,
    slug_from_url,
)


class PageExtractor:
    NOISE_SELECTORS = (
        "script",
        "style",
        "noscript",
        "iframe",
        "form",
        ".mw-editsection",
        ".toc",
        ".reflist",
        ".reference",
        ".printfooter",
        ".metadata",
        ".navbox",
        ".mbox-small",
        ".mw-empty-elt",
    )

    def __init__(self, profile: WikiSiteProfile) -> None:
        self.profile = profile
        self.allowed_domains = profile.allowed_domains
        self.allowed_prefix = profile.allowed_path_prefix

    def extract_page(
        self,
        *,
        url: str,
        slug: str,
        html: str,
        source_encoding: str | None,
        internal_link_resolver: Callable[[str], str],
        fetch_source: str = "direct_http",
    ) -> PageDocument:
        soup = BeautifulSoup(html, "lxml")

        title_node = self._select_first(soup, self.profile.title_selectors)
        title = _clean_text(title_node.get_text(" ", strip=True) if title_node else "") or slug

        categories = self._extract_categories(soup)
        content_root = self._find_content_root(soup)
        self._remove_noise(content_root)

        headings = []
        for heading in content_root.select("h2, h3, h4, h5, h6"):
            text = _clean_text(heading.get_text(" ", strip=True))
            if text:
                headings.append({"level": int(heading.name[1]), "text": text})

        paragraphs = [
            text
            for paragraph in content_root.select("p")
            if (text := _clean_text(paragraph.get_text(" ", strip=True)))
        ]

        lists = []
        for node in content_root.select("ul, ol"):
            items = [
                _clean_text(li.get_text(" ", strip=True))
                for li in node.find_all("li", recursive=False)
                if _clean_text(li.get_text(" ", strip=True))
            ]
            if items:
                lists.append(items)

        quotes = [
            text
            for node in content_root.select("blockquote")
            if (text := _clean_text(node.get_text(" ", strip=True)))
        ]

        code_blocks = []
        for node in content_root.select("pre, code"):
            text = node.get_text("\n", strip=True)
            if not text:
                continue
            normalized = text.strip()
            if normalized and normalized not in code_blocks:
                code_blocks.append(normalized)

        tables, infoboxes = self._extract_tables(content_root)
        templates = self._extract_templates(content_root)

        internal_links: list[str] = []
        external_links: list[str] = []
        seen_internal: set[str] = set()
        seen_external: set[str] = set()

        for anchor in content_root.select("a[href]"):
            raw_href = anchor.get("href", "").strip()
            canonical = canonicalize_url(
                raw_href,
                url,
                allowed_domains=self.allowed_domains,
                allowed_prefix=self.allowed_prefix,
            )
            if canonical:
                if canonical not in seen_internal:
                    seen_internal.add(canonical)
                    internal_links.append(canonical)
                anchor["href"] = internal_link_resolver(slug_from_url(canonical, self.allowed_prefix))
                continue

            absolute = make_absolute_url(raw_href, url)
            if absolute:
                anchor["href"] = absolute
                if absolute not in seen_external:
                    seen_external.add(absolute)
                    external_links.append(absolute)

        images: list[ImageRecord] = []
        for image in content_root.select("img"):
            thumb = make_absolute_url(image.get("data-src") or image.get("src"), url)
            if not thumb:
                continue

            original = derive_original_image_url(thumb)
            image["src"] = thumb
            image["data-original-src"] = original

            images.append(
                ImageRecord(
                    original_url=original,
                    thumbnail_url=thumb,
                    alt=_clean_text(image.get("alt", "")),
                    title=_clean_text(image.get("title", "")),
                    context_text=self._extract_image_context(image),
                )
            )

        cleaned_html = _serialize_fragment(content_root)
        markdown = html_to_markdown(
            cleaned_html,
            heading_style="ATX",
            bullets="-",
            strip=["script", "style", "noscript", "iframe"],
        )
        content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        plain_text = _clean_text(content_root.get_text(" ", strip=True))
        word_count = _word_count(plain_text)
        excerpt = self._build_excerpt(paragraphs, plain_text)

        return PageDocument(
            url=url,
            slug=slug,
            title=title,
            excerpt=excerpt,
            word_count=word_count,
            reading_time_minutes=(max(1, math.ceil(word_count / 220)) if word_count else 0),
            headings=headings,
            paragraphs=paragraphs,
            lists=lists,
            quotes=quotes,
            code_blocks=code_blocks,
            tables=tables,
            infoboxes=infoboxes,
            templates=templates,
            categories=categories,
            internal_links=internal_links,
            external_links=external_links,
            images=images,
            html_clean=cleaned_html,
            markdown=markdown,
            fetched_at=datetime.now(UTC).isoformat(),
            content_hash=content_hash,
            source_encoding=source_encoding,
            fetch_source=fetch_source,
        )

    def _extract_categories(self, soup: BeautifulSoup) -> list[str]:
        categories: list[str] = []
        seen: set[str] = set()
        for selector in self.profile.category_selectors:
            for anchor in soup.select(selector):
                label = _clean_text(anchor.get_text(" ", strip=True))
                if not label or label.lower() in {"categorias", "categoria"}:
                    continue
                if label not in seen:
                    seen.add(label)
                    categories.append(label)
        return categories

    def _find_content_root(self, soup: BeautifulSoup) -> Tag:
        node = self._select_first(soup, self.profile.content_root_selectors)
        if node:
            return node
        if soup.body:
            return soup.body
        return soup

    def _remove_noise(self, content_root: Tag) -> None:
        for selector in self.NOISE_SELECTORS + tuple(self.profile.extra_noise_selectors):
            for node in content_root.select(selector):
                node.decompose()
        for comment in content_root.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        for wrapper in content_root.select("html, body"):
            wrapper.unwrap()
        for node in content_root.select("[style*='display:none'], [style*='display: none']"):
            node.decompose()
        for node in content_root.select(".mw-parser-output > .mw-parser-output:only-child"):
            node.unwrap()
        for node in content_root.select("span[id^='toc'], .mw-headline"):
            if node.name == "span" and node.parent and node.parent.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                node.unwrap()

    def _build_excerpt(self, paragraphs: list[str], plain_text: str) -> str:
        source = ""
        for paragraph in paragraphs:
            if len(paragraph) >= 60:
                source = paragraph
                break
            if not source and paragraph:
                source = paragraph
        if not source:
            source = plain_text
        if len(source) <= 240:
            return source
        return source[:237].rstrip() + "..."

    def _extract_tables(self, content_root: Tag) -> tuple[list[dict], list[dict]]:
        tables: list[dict] = []
        infoboxes: list[dict] = []

        for index, table in enumerate(content_root.select("table")):
            classes = [class_name for class_name in table.get("class", []) if class_name]
            caption_node = table.find("caption")
            caption = _clean_text(caption_node.get_text(" ", strip=True) if caption_node else "")

            headers: list[str] = []
            rows: list[list[str]] = []
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                if not cells:
                    continue
                values = [_clean_text(cell.get_text(" ", strip=True)) for cell in cells]
                values = [value for value in values if value]
                if not values:
                    continue
                if row.find_all("th") and not headers:
                    headers = values
                else:
                    rows.append(values)

            tables.append(
                {
                    "index": index,
                    "caption": caption,
                    "classes": classes,
                    "headers": headers,
                    "rows": rows,
                }
            )

            if any("infobox" in class_name.lower() for class_name in classes):
                info: dict[str, str] = {}
                for row in table.find_all("tr"):
                    header = row.find("th")
                    value = row.find("td")
                    if not header or not value:
                        continue
                    key = _clean_text(header.get_text(" ", strip=True))
                    parsed_value = _clean_text(value.get_text(" ", strip=True))
                    if key and parsed_value:
                        info[key] = parsed_value
                if info:
                    infoboxes.append(info)

        return tables, infoboxes

    def _extract_templates(self, content_root: Tag) -> list[dict]:
        templates: list[dict] = []
        seen: set[tuple[str, str]] = set()

        for node in content_root.select("[class]"):
            classes = [class_name for class_name in node.get("class", []) if class_name]
            template_classes = [
                class_name
                for class_name in classes
                if "template" in class_name.lower() or "navbox" in class_name.lower()
            ]
            if not template_classes:
                continue

            text_preview = _clean_text(node.get_text(" ", strip=True))[:280]
            key = ("|".join(sorted(template_classes)), text_preview)
            if key in seen:
                continue
            seen.add(key)
            templates.append({"classes": template_classes, "preview": text_preview})

        return templates

    def _extract_image_context(self, image: Tag) -> str:
        for parent in image.parents:
            if isinstance(parent, Tag) and parent.name in {"figure", "div", "td", "p"}:
                text = _clean_text(parent.get_text(" ", strip=True))
                if text:
                    return text[:220]
        return ""

    def _select_first(self, soup: BeautifulSoup | Tag, selectors: tuple[str, ...]) -> Tag | None:
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                return node
        return None


def _clean_text(text: str) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def _serialize_fragment(node: Tag) -> str:
    if node.name in {"html", "body"}:
        return "".join(str(child) for child in node.contents)
    return str(node)


def _word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))
