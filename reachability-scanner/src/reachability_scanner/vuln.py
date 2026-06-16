import json
from typing import Any

def load_vulns(path: str) -> list[dict[str, Any]]:
    with open(path) as f:
        return json.load(f)

def filter_reachable(reachable: set[str], vulns: list[dict]) -> list[str]:
    hits = []
    for v in vulns:
        if any(func in reachable for func in v.get("functions", [])):
            hits.append(v["id"])
    return hits