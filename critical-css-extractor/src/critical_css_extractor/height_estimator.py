from bs4 import BeautifulSoup, Tag
from bs4.element import ContentsList
from typing import Dict, Any

AVERAGE_HEIGHTS: Dict[str, int] = {
    "h1": 48,
    "h2": 36,
    "h3": 28,
    "h4": 24,
    "h5": 20,
    "h6": 18,
    "p": 22,
    "div": 32,
    "span": 18,
    "header": 60,
    "nav": 50,
    "main": 40,
    "section": 40,
    "article": 40,
    "aside": 35,
    "footer": 45,
    "ul": 25,
    "ol": 25,
    "li": 22,
    "a": 20,
    "img": 200,
    "figure": 220,
    "blockquote": 50,
    "table": 30,
    "tr": 25,
    "td": 25,
    "form": 35,
    "input": 40,
    "button": 40,
    "label": 22,
}


def estimate_height(tag: str, attrs: Dict[str, Any]) -> int:
    """Estimate element height in px."""
    return AVERAGE_HEIGHTS.get(tag.lower(), 25)


def mark_above_fold(soup: BeautifulSoup, viewport_height: int = 800) -> None:
    """Traverse DOM, mark above-fold elements with data-critical=1. Modifies soup in-place."""
    current_height = 0

    def traverse(element: Any) -> bool:
        nonlocal current_height
        if current_height > viewport_height * 1.2:  # 20% buffer
            return False

        if isinstance(element, Tag):
            tag = element.name
            if tag:
                height = estimate_height(tag, dict(element.attrs))
                current_height += height
                if current_height <= viewport_height:
                    element["data-critical"] = "1"

                for child in element.children:
                    if not traverse(child):
                        return False
        elif isinstance(element, ContentsList):
            for child in element:
                if not traverse(child):
                    return False
        return True

    body = soup.find("body") or soup.find("html")
    if body:
        traverse(body)