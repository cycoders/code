from typing import Dict, Any, List

from .scanner import StatsEntry


def suggest_globs(
    stats: Dict[str, StatsEntry],
    coverage_target: float = 0.95,
    max_globs: int = 10,
) -> List[str]:
    """Suggest minimal globs covering target coverage of large bytes."""
    if not stats:
        return []

    total_bytes = sum(s["total_size"] for s in stats.values())
    sorted_exts = sorted(
        stats.items(),
        key=lambda item: item[1]["total_size"],
        reverse=True,
    )

    globs: List[str] = []
    cumulative_bytes = 0

    for ext, entry in sorted_exts:
        glob = f"*{ext}"
        globs.append(glob)
        cumulative_bytes += entry["total_size"]
        coverage = cumulative_bytes / total_bytes
        if coverage >= coverage_target or len(globs) >= max_globs:
            break

    return globs
