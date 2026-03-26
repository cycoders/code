from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

TECH_PATTERNS = {
    "Nginx": {"headers": ["nginx"], "confidence": "high"},
    "Apache": {"headers": ["apache"], "confidence": "high"},
    "PHP": {"headers": ["x-powered-by", "php"], "confidence": "high"},
    "Node.js": {"headers": ["x-powered-by", "express"], "confidence": "medium"},
    "React": {"html": ["react", "_next"], "confidence": "high"},
    "Vue.js": {"html": ["vue"], "confidence": "high"},
    "Angular": {"html": ["angular"], "confidence": "high"},
    "jQuery": {"html": ["jquery"], "confidence": "high"},
    "Bootstrap": {"html": ["bootstrap"], "confidence": "high"},
    "WordPress": {"html": ["wp-content"], "confidence": "high"},
    # Add more
}


def detect_tech(headers: Dict[str, str], html: Optional[str] = None) -> List[Dict[str, str]]:
    """Detect tech stack."""
    matches = []
    lower_headers = {k.lower(): v.lower() for k, v in headers.items()}

    for name, pattern in TECH_PATTERNS.items():
        score = 0
        signals = []
        if "headers" in pattern:
            for h in pattern["headers"]:
                if any(h in v for v in lower_headers.values()):
                    score += 1
                    signals.append("header")
        if html and "html" in pattern:
            soup = BeautifulSoup(html, "lxml")
            for h in pattern["html"]:
                if h in html.lower() or soup.find(attrs={"name": "generator", "content": lambda c: h in c.lower() if c else False}):
                    score += 1
                    signals.append("html")
        if score > 0:
            conf = pattern["confidence"]
            matches.append({"name": name, "confidence": conf, "signals": signals})

    return sorted(matches, key=lambda x: ("high" if x["confidence"] == "high" else "low", x["name"]))