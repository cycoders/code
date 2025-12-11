import yaml
import pandas as pd
from pathlib import Path
from typing import Optional

from rich.console import Console

from .types import Config

console = Console()


def load_config(config_path: Optional[Path]) -> Config:
    config: Config = {
        "default_mode": "fake",
        "threshold": 0.05,
        "patterns": {},
        "anonymizers": {},
        "salt": None
    }
    if config_path and config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    return config


def load_dataframe(path: Path, format: str = "auto") -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        console.print(f"[red]Error: File {path} not found.[/red]")
        raise FileNotFoundError(path)

    try:
        if format == "auto":
            if path.suffix == ".csv":
                return pd.read_csv(path)
            elif path.suffix in [".json", ".ndjson", ".jsonl"]:
                if path.suffix == ".json":
                    return pd.read_json(path)
                else:
                    return pd.read_json(path, lines=True)
            else:
                raise ValueError(f"Unknown format: {path.suffix}")
        elif format == "csv":
            return pd.read_csv(path)
        elif format == "json":
            return pd.read_json(path, lines=True)
    except Exception as e:
        console.print(f"[red]Error loading {path}: {e}[/red]")
        raise


def save_dataframe(df: pd.DataFrame, path: Path, fmt: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "json":
        df.to_json(path, orient="records", lines=True, indent=2)
    console.print(f"[green]Saved to {path}[/green]")
