import subprocess
import time
from pathlib import Path
from typing import List

import rich.progress
from rich.console import Console

from .types import Times


console = Console()


def run_benchmark(
    command: List[str],
    iterations: int = 10,
    warmup: int = 2,
    timeout: float = 60.0,
) -> Times:
    if not command:
        raise ValueError("Command cannot be empty")

    script_path = Path(command[0])
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    times: Times = []

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Warmup
        if warmup > 0:
            task = progress.add_task("Warming up...", total=warmup)
            for _ in range(warmup):
                _run_once(command, timeout)
                progress.advance(task)
            progress.remove_task(task)

        # Benchmark
        task = progress.add_task("Benchmarking...", total=iterations)
        for i in range(iterations):
            try:
                start = time.perf_counter()
                proc = _run_once(command, timeout)
                end = time.perf_counter()
                times.append(end - start)
            except subprocess.TimeoutExpired:
                raise TimeoutError(f"Command timed out after {timeout}s (iteration {i+1})")
            progress.advance(task)

    return times


def _run_once(command: List[str], timeout: float) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        command,
        timeout=timeout,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed (code {proc.returncode}):\n{proc.stderr}"
        )
    return proc