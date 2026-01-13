import json
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup


def extract_meta(soup: BeautifulSoup, prefix: str) -> Dict[str, str]:
    """Extract meta tags matching prefix (e.g., 'og:', 'twitter:')."""
    result: Dict[str, str] = {}
    for meta in soup.find_all("meta", property=lambda p: p and p.startswith(prefix)):
        prop = meta.get("property")
        if prop:
            key = prop[len(prefix) :].replace("-", "_").lower()
            content = meta.get("content", "").strip()
            if content:
                result[key] = content
    return result


def parse_ogp(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse Open Graph meta tags."""
    return extract_meta(soup, "og:")


def parse_twitter(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse Twitter Card meta tags."""
    return extract_meta(soup, "twitter:")


def parse_basic(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse basic <title> and <meta name="description">."""
    result: Dict[str, str] = {}
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        result["title"] = title_tag.string.strip()
    desc_meta = soup.find("meta", attrs={"name": "description"})
    if desc_meta and desc_meta.get("content"):
        result["description"] = desc_meta.get("content").strip()
    return result


def parse_jsonld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse Schema.org JSON-LD scripts."""
    jsonlds: List[Dict[str, Any]] = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        if script.string:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    jsonlds.extend(data)
                else:
                    jsonlds.append(data)
            except json.JSONDecodeError:
                pass
    return jsonlds


def get_jsonld_prop(jsonlds: List[Dict[str, Any]], fields: List[str]) -> Optional[str]:
    """Extract first matching property from JSON-LD."""
    for jd in jsonlds:
        for field in fields:
            val = jd.get(field)
            if val:
                if isinstance(val, str):
                    return val.strip()
                elif isinstance(val, (list, dict)):
                    return str(val).strip()
    return None
