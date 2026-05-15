from collections import defaultdict
from typing import Any


def estimate_cardinality(metrics: list[dict], threshold: int = 1000) -> list[dict[str, Any]]:
    by_name: dict[str, set] = defaultdict(set)
    for m in metrics:
        key = tuple(sorted(m["labels"].items()))
        by_name[m["name"]].add(key)
    results = []
    for name, combos in by_name.items():
        card = len(combos)
        if card >= threshold:
            results.append({"metric": name, "cardinality": card, "severity": "high" if card > threshold * 5 else "medium"})
    return sorted(results, key=lambda x: -x["cardinality"])