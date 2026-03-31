from pathlib import Path
import csv
import random
from typing import Callable, List, Dict, Any

def load_durations(file_path: Path) -> List[float]:
    """Load service durations from CSV (one or more per row)."""
    if not file_path.exists():
        raise FileNotFoundError(f"Service file not found: {file_path}")
    durations: List[float] = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for val in row:
                try:
                    durations.append(float(val))
                except ValueError:
                    pass  # skip invalid
    if not durations:
        raise ValueError("No valid durations found in CSV")
    return durations

def get_service_sampler(
    dist_type: str, params: Dict[str, Any], rng: random.Random
) -> Callable[[], float]:
    """Return a sampler function: () -> service_time."""
    if dist_type == "fixed":
        mean = params["service_mean"]
        return lambda: float(mean)
    elif dist_type == "exp":
        rate = 1.0 / params["service_mean"]
        return lambda: rng.expovariate(rate)
    elif dist_type == "empirical":
        durations = load_durations(params["service_file"])
        return lambda: rng.choices(population=durations, k=1)[0]
    else:
        raise ValueError(f"Unknown dist: {dist_type}")