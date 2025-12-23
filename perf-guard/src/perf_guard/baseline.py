import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .stats import Stats
from .types import Stats


BASELINE_DIR = Path(".perfguard-baselines")


def get_baseline_path(name: str) -> Path:
    BASELINE_DIR.mkdir(exist_ok=True)
    return BASELINE_DIR / f"{name}.json"


def load_baseline(name: str) -> Optional[Stats]:
    path = get_baseline_path(name)
    if not path.exists():
        return None

    with open(path, "r") as f:
        data: Dict[str, Any] = json.load(f)

    # Basic validation
    required = {"mean", "stdev", "min", "max", "iterations", "unit"}
    if not required.issubset(data):
        raise ValueError(f"Invalid baseline format in {path}")

    return data  # type: ignore


def save_baseline(name: str, stats: Stats, command: str) -> None:
    path = get_baseline_path(name)
    data = {
        **stats,
        "command": command,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)