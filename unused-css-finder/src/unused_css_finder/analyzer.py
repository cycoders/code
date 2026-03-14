import logging
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup
from cssutils import CSSParser, CSSRule


def load_html_files(html_paths: List[Path]) -> List[BeautifulSoup]:
    html_files: List[Path] = []
    for p in html_paths:
        if p.is_file():
            html_files.append(p)
        elif p.is_dir():
            html_files.extend(p.rglob("*.html"))
            html_files.extend(p.rglob("*.htm"))
    soups = []
    for f in html_files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                soups.append(BeautifulSoup(fh, "lxml"))
        except Exception as e:
            logging.warning(f"Skipping {f}: {e}")
    return soups


def get_all_style_rules(sheet) -> List[CSSRule]:
    """Recursively collect all STYLE_RULE from sheet and nested rules."""
    style_rules = []
    def recurse(rules):
        for rule in rules:
            if rule.type == CSSRule.STYLE_RULE:
                style_rules.append(rule)
            if hasattr(rule, "cssRules") and rule.cssRules:
                recurse(rule.cssRules)
    recurse(sheet.cssRules)
    return style_rules


def analyze_css_file(css_path: str, soups: List[BeautifulSoup]) -> List[Dict]:
    """Analyze CSS file, return dicts for each style rule."""
    parser = CSSParser()
    sheet = parser.parseFile(css_path)
    style_rules = get_all_style_rules(sheet)

    results: List[Dict] = []
    for rule in style_rules:
        selector_text = rule.selectorText
        used = any(soup.select(selector_text) for soup in soups)
        rule_size = len(rule.cssText.encode("utf-8"))
        results.append({
            "selector": selector_text,
            "cssText": rule.cssText,
            "size": rule_size,
            "used": used,
        })
    return results


def purge_used_css(results: List[Dict], output_path: Path):
    """Write flattened used CSS rules to file."""
    used_css = "\n".join(r["cssText"].rstrip("\n") for r in results if r["used"])
    output_path.write_text(used_css + "\n", encoding="utf-8")
