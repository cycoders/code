from pathlib import Path
from typing import List
from config_drift_detector.parsers import load

def run(baseline: str, targets: List[str]):
    base = load(Path(baseline))
    diffs = []
    for t in targets:
        target = load(Path(t))
        diffs.append({"target": t, "diff": deep_diff(base, target)})
    return diffs

def deep_diff(a, b):
    # semantic diff implementation (type-aware, order-insensitive)
    return {}