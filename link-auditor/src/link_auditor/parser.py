import re
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import markdown


def is_checkable_link(href: str) -> bool:
    """Filter non-HTTP links."""
    lower_href = href.lower()
    if lower_href.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return False
    return True


def extract_links_from_html(html_content: str, base_url: str | None = None) -> List[str]:
    """Extract <a href> from HTML."""
    soup = BeautifulSoup(html_content, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if is_checkable_link(href):
            full_url = urljoin(base_url or "", href)
            links.append(full_url)
    return links


def extract_links_from_md(md_content: str, base_url: str | None = None) -> List[str]:
    """Render MD to HTML and extract links."""
    html = markdown.markdown(md_content)
    return extract_links_from_html(html, base_url)


def extract_urls_from_sitemap(xml_content: str) -> List[str]:
    """Parse sitemap XML for <loc>."""
    from xml.etree import ElementTree as ET

    try:
        root = ET.fromstring(xml_content)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = root.findall(".//s:loc", ns)
        return [loc.text.strip() for loc in locs if loc.text]
    except ET.ParseError:
        return []
