import json
import os
from pathlib import Path
from typing import Dict, Literal, Optional

import git
import typer
from git import Repo

from .measure import BenchmarkResult, MetricName

_BASELINE_DIR = Path(".perf-regression")
_BASELINE_FILE = _BASELINE_DIR / "baseline.json"


def _ensure_dir():
    _BASELINE_DIR.mkdir(exist_ok=True)


def load_baseline(ref: Optional[str] = None) -> Optional[BenchmarkResult]:
    """Load baseline from current dir or git ref."""
    _ensure_dir()

    if not ref:
        if _BASELINE_FILE.exists():
            with open(_BASELINE_FILE) as f:
                return json.load(f)
        return None

    try:
        repo = Repo(Path.cwd(), search_parent_directories=True)
        if ref not in repo.refs:
            # Try tag/branch
            pass
        content = repo.git.show(f"{ref}:{_BASELINE_FILE}")
        data = json.loads(content)
        return data
    except Exception as e:
        typer.echo(f"[yellow]Baseline {ref} not found: {e}[/yellow]")
        return None


def save_baseline(results: BenchmarkResult, path: Path):
    """Save results as baseline JSON."""
    _ensure_dir()
    with open(path, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)


def update_baseline_file(new_results: BenchmarkResult):
    """Update .perf-regression/baseline.json."""
    save_baseline(new_results, _BASELINE_FILE)