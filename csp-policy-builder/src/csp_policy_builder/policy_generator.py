from collections import defaultdict
from typing import Dict, List

from .types import Resource


def generate_csp(resources: List[Resource], prefer_hashes: bool = True) -> str:
    """Generate CSP string from resources."""
    directives: Dict[str, List[str]] = defaultdict(list)

    for res in resources:
        if res.is_inline:
            if prefer_hashes and res.hash_value:
                directives[res.directive].append(res.hash_value)
            else:
                directives[res.directive].append("'unsafe-inline'")
        else:
            if res.scheme in ("http", "https"):
                if res.host:
                    directives[res.directive].append(res.host)
                else:
                    directives[res.directive].append("*")
            elif res.scheme == "data":
                directives[res.directive].append("'data'")
            elif res.scheme == "blob":
                directives[res.directive].append("'blob'")
            else:
                directives[res.directive].append("*")

    # Dedupe, sort
    policy_parts = []
    for directive in sorted(directives):
        srcs = sorted(set(directives[directive]))
        policy_parts.append(f"{directive} {' '.join(srcs)}")

    return "; ".join(policy_parts)


def strictness_score(policy: str) -> int:
    """0-100 score: more directives + no unsafe/* = higher."""
    score = 50  # base
    parts = policy.split(";")
    num_directives = len([p for p in parts if p.strip()])
    score += num_directives * 4

    penalties = 0
    if "'unsafe-inline'" in policy:
        penalties += 20
    if "*" in policy:
        penalties += 10 * policy.count("*")
    if "'unsafe-eval'" in policy:
        penalties += 30

    return max(0, min(100, score - penalties))
