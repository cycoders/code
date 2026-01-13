import os
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
from requests_cache import CachedSession
from requests.exceptions import RequestException

from .models import Metadata
from .parser import (
    parse_ogp,
    parse_twitter,
    parse_basic,
    parse_jsonld,
    get_jsonld_prop,
)


def fetch_metadata(
    url: str,
    user_agent: Optional[str] = None,
    timeout: int = 10,
    cache_dir: str = "~/.cache/link-metadata-cli",
    cache_expire: int = 3600,
    use_cache: bool = True,
) -> Metadata:
    """Fetch and parse link metadata from URL."""
    cache_path = Path(cache_dir).expanduser()
    cache_path.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": user_agent
        or "LinkMetadataCLI/0.1.0 (+https://github.com/cycoders/code/tree/main/link-metadata-cli)",
    }

    session: requests.Session
    if use_cache:
        session = CachedSession(
            cache_name="http_cache",
            cache_dir=str(cache_path),
            expire_after=cache_expire,
            ignored_headers=["User-Agent"],
        )
    else:
        session = requests.Session()

    try:
        resp = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()

        soup = resp.html.parser  # Wait, resp.content
        No:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        # Parse sources
        ogp = parse_ogp(soup)
        twitter = parse_twitter(soup)
        basic = parse_basic(soup)
        jsonlds = parse_jsonld(soup)

        # Merge with priority
        title_fields = ["title"]
        title = (
            ogp.get("title")
            or twitter.get("title")
            or get_jsonld_prop(jsonlds, ["headline", "name", "title"])
            or basic.get("title")
        )

        desc_fields = ["description"]
        description = (
            ogp.get("description")
            or twitter.get("description")
            or get_jsonld_prop(jsonlds, ["description"])
            or basic.get("description")
        )

        image_candidates = [ogp.get("image"), twitter.get("image")]
        image = None
        for img in image_candidates:
            if img:
                image = urllib.parse.urljoin(resp.url, img)
                break
        if not image:
            image = get_jsonld_prop(jsonlds, ["image", "thumbnail_url", "thumbnailUrl"])
            if image:
                image = urllib.parse.urljoin(resp.url, image)

        site_name = (
            ogp.get("site_name")
            or twitter.get("site")
            or get_jsonld_prop(jsonlds, ["publisher", "site_name"])
        )

        typ = ogp.get("type") or twitter.get("card")

        twitter_card = twitter.get("card")

        raw = {
            "ogp": ogp,
            "twitter": twitter,
            "basic": basic,
            "jsonld": jsonlds,
        }

        data = {
            "url": resp.url,
            "title": title,
            "description": description,
            "image": image,
            "site_name": site_name,
            "type": typ,
            "twitter_card": twitter_card,
            "raw": raw,
        }

        return Metadata.model_validate(data)

    except RequestException as e:
        raise RuntimeError(f"Failed to fetch {url}: {str(e)}") from e
    finally:
        if not use_cache:
            session.close()
