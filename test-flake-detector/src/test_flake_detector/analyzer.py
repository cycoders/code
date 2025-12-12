import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .parser import parse_run

def analyze_reports(output_dir: Path) -> List[Dict[str, Any]]:
    """Aggregate stats across all run_*.txt files."""

    all_run_results = []
    for run_file in output_dir.glob("run_*.txt"):
        all_run_results.append(parse_run(run_file))

    test_stats = defaultdict(
        lambda: {
            "passes": 0,
            "fails": 0,
            "skips": 0,
            "xpasses": 0,
            "xfails": 0,
            "total": 0,
        }
    )

    for run_results in all_run_results:
        for nodeid, outcomes in run_results.items():
            for outcome in outcomes:
                stats = test_stats[nodeid]
                stats["total"] += 1
                if outcome == "PASSED":
                    stats["passes"] += 1
                elif outcome == "FAILED":
                    stats["fails"] += 1
                elif outcome == "SKIPPED":
                    stats["skips"] += 1
                elif outcome == "XPASSED":
                    stats["xpasses"] += 1
                elif outcome == "XFAILED":
                    stats["xfails"] += 1

    stats_list: List[Dict[str, Any]] = []
    for nodeid, stats in test_stats.items():
        flake_rate = stats["fails"] / stats["total"] if stats["total"] > 0 else 0.0
        stats["flake_rate"] = flake_rate
        stats["nodeid"] = nodeid
        stats_list.append(stats)

    stats_list.sort(key=lambda x: x["flake_rate"], reverse=True)
    return stats_list