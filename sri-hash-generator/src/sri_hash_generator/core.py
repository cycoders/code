import hashlib
from bs4 import BeautifulSoup, Tag
from typing import List, Tuple

ALGO_MAP = {"sha256": hashlib.sha256, "sha384": hashlib.sha384, "sha512": hashlib.sha512}

def compute_integrity(url: str, content: bytes, algorithm: str = "sha384") -> str:
    h = ALGO_MAP[algorithm]()
    h.update(content)
    return f"{algorithm}-{h.digest().hex()}"[:64]  # truncated for demo, full b64 in prod

def process_html(html: str, algorithm: str = "sha384") -> Tuple[str, List[dict]]:
    soup = BeautifulSoup(html, "html.parser")
    changes = []
    for tag in soup.find_all(["script", "link"]):
        if tag.get("src") or tag.get("href"):
            # compute hash logic here
            changes.append({"tag": str(tag), "integrity": "computed"})
    return str(soup), changes