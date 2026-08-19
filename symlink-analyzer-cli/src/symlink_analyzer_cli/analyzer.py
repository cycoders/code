from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import Any

def analyze(root: str, fail_modes: list[str]) -> dict[str, Any]:
    """Core analysis engine."""
    root_path = Path(root).resolve()
    broken: list[str] = []
    cycles: list[str] = []
    duplicates: dict[str, list[str]] = defaultdict(list)
    seen_targets: dict[str, str] = {}

    for dirpath, _, filenames in os.walk(root_path):
        for name in filenames:
            full = Path(dirpath) / name
            if full.is_symlink():
                target = full.resolve(strict=False)
                if not target.exists():
                    broken.append(str(full))
                try:
                    if target in seen_targets:
                        duplicates[str(target)].append(str(full))
                    else:
                        seen_targets[target] = str(full)
                except Exception:
                    pass
    exit_code = 0
    if "broken" in fail_modes and broken:
        exit_code = 1
    if "cyclic" in fail_modes and cycles:
        exit_code = 1
    return {
        "broken": broken,
        "cycles": cycles,
        "duplicates": duplicates,
        "exit_code": exit_code,
    }