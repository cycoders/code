import re
import requests
import cssutils
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from typing import List

cssutils.log.setLevel(60)  # Suppress cssutils logs


def get_all_css_sources(
    soup: BeautifulSoup,
    html_path: Path | None,
    css_files: List[Path],
    include_inline: bool,
) -> List[str]:
    """Gather all CSS: files, linked, inline."""
    sources: List[str] = []

    # Explicit CSS files
    for css_file in css_files:
        sources.append(css_file.read_text(encoding="utf-8"))

    # Linked stylesheets
    for link in soup.find_all("link", rel="stylesheet"):
        href: str | None = link.get("href")
        if href:
            try:
                if href.startswith(("http://", "https://")):
                    resp = requests.get(href, timeout=5)
                    resp.raise_for_status()
                    sources.append(resp.text)
                elif html_path:
                    css_path = html_path.parent / href
                    sources.append(css_path.read_text(encoding="utf-8"))
            except Exception:
                pass  # Skip broken links

    # Inline styles
    if include_inline:
        for style_tag in soup.find_all("style"):
            if style_tag.string:
                sources.append(style_tag.string)

    return sources


def load_rules(css_sources: List[str]) -> List['cssutils.css.StyleRule']:
    """Parse CSS sources into style rules."""
    rules = []
    for css_text in css_sources:
        sheet = cssutils.parseString(css_text)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                rules.append(rule)
    return rules


def minify_css(css: str) -> str:
    """Minify CSS: remove comments, whitespace, etc."""
    # Remove comments
    css = re.sub(r"\s*[/][*][^\n]*[*][/]\s*", "", css, flags=re.MULTILINE | re.DOTALL)
    # Normalize whitespace
    css = re.sub(r"\s+", " ", css)
    # Collapse around symbols
    css = re.sub(r"\s*([{:;,}] )\s*", r"\1", css)
    # Semicolon before }
    css = css.replace(";}", "}")
    return css.strip()