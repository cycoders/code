import os
from pathlib import Path
from typing import List, Tuple, Set
from urllib.parse import urljoin

import httpx

from .parser import extract_links_from_html, extract_links_from_md, extract_urls_from_sitemap

from .settings import Settings


def collect_links(inputs: List[str], settings: Settings) -> List[str]:
    """Collect all unique checkable links from inputs."""
    all_links: Set[str] = set()

    for inp in inputs:
        if os.path.isdir(inp):
            _collect_from_dir(inp, all_links, settings)
        elif os.path.isfile(inp):
            _collect_from_file(inp, all_links)
        elif inp.startswith("http"):
            _collect_from_url(inp, all_links)

    filtered = [url for url in all_links if settings.filter_link(url)]
    return list(set(filtered))  # dedupe


def _collect_from_dir(dir_path: str, all_links: Set[str], settings: Settings):
    dirpath = Path(dir_path)
    for file_path in dirpath.rglob("*.md"):
        _collect_from_file(str(file_path), all_links)
    for file_path in dirpath.rglob("*.html"):
        _collect_from_file(str(file_path), all_links)


def _collect_from_file(file_path: str, all_links: Set[str]):
    base_url = Path(file_path).parent.as_posix() + "/"
    try:
        text = Path(file_path).read_text(encoding="utf-8")
        if file_path.endswith(".md"):
            links = extract_links_from_md(text, base_url)
        else:
            links = extract_links_from_html(text, base_url)
        all_links.update(links)
    except Exception:
        pass  # silent skip corrupt files


def _collect_from_url(url: str, all_links: Set[str]):
    try:
        resp = httpx.get(url, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        if "sitemap" in resp.url.path.lower():
            links = extract_urls_from_sitemap(resp.text)
        else:
            links = extract_links_from_html(resp.text, str(resp.url))
        all_links.update(links)
    except Exception:
        pass  # skip unreachable
