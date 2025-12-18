import tomllib
from pathlib import Path
from typing import List
from .types import Config


def load_config(
    target_dir: str,
    config_file: str | None,
    exclude: List[str],
    pytest_args: List[str],
    timeout: int,
    max_mutants: int,
    min_score: float,
    dry_run: bool,
) -> Config:
    cfg = Config(
        target_dir=Path(target_dir),
        exclude_patterns=exclude,
        pytest_args=pytest_args,
        timeout_secs=timeout,
        max_mutants=max_mutants,
        min_score_pct=min_score,
        dry_run=dry_run,
    )

    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            for key, val in data.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, val)
    return cfg