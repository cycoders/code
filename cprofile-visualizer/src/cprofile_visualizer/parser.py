import pstats
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pstats import Stats


def load_profile(prof_path: Path) -> "pstats.Stats":
    """
    Load and prepare pstats.Stats: strip dirs, validate non-empty.
    """
    if not prof_path.exists():
        raise FileNotFoundError(f"Profile not found: {prof_path}")

    stats: pstats.Stats = pstats.Stats(str(prof_path))
    stats.strip_dirs()  # Clean paths

    if len(stats.stats) == 0:
        raise ValueError("Empty profile: no stats found.")

    return stats


def get_sort_key(sort_str: str) -> str:
    """
    Map CLI sort to pstats.sort_stats arg.
    """
    mapping = {
        "cumtime": "cumulative",
        "tottime": "time",
        "calls": "calls",
        "filename": "filename",
        "name": "name",
        "line": "line",
    }
    return mapping.get(sort_str, sort_str)
