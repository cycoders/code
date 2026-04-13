import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List

from .height_estimator import mark_above_fold
from .css_utils import load_rules, minify_css, get_all_css_sources


def is_url(input_str: str) -> bool:
    return input_str.startswith(("http://", "https://"))


def get_html_content(html_input: str) -> tuple[str, Optional[Path]]:
    """Fetch HTML from file or URL."""
    if is_url(html_input):
        resp = requests.get(html_input, timeout=10)
        resp.raise_for_status()
        html_path = None
    else:
        path = Path(html_input)
        html = path.read_text(encoding="utf-8")
        html_path = path
    return resp.text if is_url(html_input) else html_input.read_text(), html_path


def extract_critical_css(
    html_input: str,
    css_files: List[Path],
    viewport_height: int,
    include_inline: bool,
) -> str:
    """Main extraction logic."""
    html_content, html_path = get_html_content(html_input)

    soup = BeautifulSoup(html_content, features="lxml")
    mark_above_fold(soup, viewport_height)

    css_sources = get_all_css_sources(
        soup, html_path, css_files, include_inline
    )

    rules = load_rules(css_sources)

    critical_rules = [
        rule for rule in rules if _rule_matches_critical(rule, soup)
    ]

    css_text = "".join(rule.cssText for rule in critical_rules)
    return minify_css(css_text)


def _rule_matches_critical(rule: 'cssutils.css.StyleRule', soup: BeautifulSoup) -> bool:
    """Check if CSS rule matches any critical element."""
    try:
        matched_elements = soup.select(rule.selectorText)
        return any(el.get("data-critical") == "1" for el in matched_elements)
    except Exception:
        return False  # Invalid selector, skip