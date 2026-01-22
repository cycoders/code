import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal


@dataclass
class Benchmark:
    name: str
    command: str
    args: List[str]
    iterations: int = 50
    timeout: float = 30.0
    metrics: List[Literal["wall_time", "cpu_time", "peak_memory"]] = field(
        default_factory=lambda: ["wall_time", "cpu_time", "peak_memory"]
    )


def load_config(config_path: Path) -> List[Benchmark]:
    """Load benchmarks from YAML config."""
    if not config_path.exists():
        raise typer.Exit(f"Config {config_path} not found. Run 'init'.")
    with open(config_path) as f:
        data = yaml.safe_load(f)
    benchmarks = []
    for b in data.get("benchmarks", []):
        benchmarks.append(Benchmark(**b))
    if not benchmarks:
        raise typer.Exit("No benchmarks in config.")
    return benchmarks