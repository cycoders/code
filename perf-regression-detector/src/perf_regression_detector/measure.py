import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Optional, Tuple

import psutil
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Benchmark


MetricName = Literal["wall_time", "cpu_time", "peak_memory"]
MetricValue = Dict[str, float]
BenchmarkResult = Dict[str, Dict[MetricName, MetricValue]]


def run_single(
    benchmark: Benchmark,
) -> Tuple[float, float, float, int, Optional[str]]:
    """Run one iteration, return (wall_s, cpu_s, peak_mb, returncode, error)."""
    cmd = [benchmark.command, *benchmark.args]

    start_wall = time.perf_counter()
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        # Close fds for isolation
        close_fds=True,
    )

    peak_mem_mb = 0.0
    poll_start = time.perf_counter()

    while p.poll() is None:
        elapsed = time.perf_counter() - poll_start
        if elapsed > benchmark.timeout:
            p.terminate()
            p.wait(5)
            return 0, 0, 0, -9, "TIMEOUT"

        try:
            proc = psutil.Process(p.pid)
            peak_mem_mb = max(peak_mem_mb, proc.memory_info().rss / 1024**2)
            for child in proc.children(recursive=True):
                try:
                    peak_mem_mb = max(
                        peak_mem_mb, child.memory_info().rss / 1024**2
                    )
                except psutil.NoSuchProcess:
                    pass
        except psutil.NoSuchProcess:
            pass
        time.sleep(0.05)  # 20Hz poll

    wall_time = time.perf_counter() - start_wall

    cpu_user = 0.0
    cpu_system = 0.0
    try:
        ct = psutil.Process(p.pid).cpu_times()
        cpu_user = ct.user
        cpu_system = ct.system
    except psutil.NoSuchProcess:
        pass
    cpu_time = cpu_user + cpu_system

    rc = p.returncode
    error = None if rc == 0 else f"RC={rc}"

    return wall_time, cpu_time, peak_mem_mb, rc, error


def compute_stats(values: List[float]) -> Dict[str, float]:
    if len(values) < 2:
        return {"mean": values[0], "std": 0.0, "min": values[0], "max": values[0]}
    return {
        "mean": mean(values),
        "std": stdev(values),
        "min": min(values),
        "max": max(values),
    }


def run_benchmarks(
    benchmarks: List[Benchmark], verbose: bool = False
) -> BenchmarkResult:
    """Run all benchmarks, return aggregated stats."""
    results: BenchmarkResult = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=typer.console,
    ) as progress:
        for bench in benchmarks:
            task = progress.add_task(f"[{bench.name}] {{task.completed}}/{{task.total}}", total=bench.iterations)

            wall_times: List[float] = []
            cpu_times: List[float] = []
            mems: List[float] = []
            errors = []

            for _ in range(bench.iterations):
                wall, cpu, mem, rc, err = run_single(bench)
                if err:
                    errors.append(err)
                else:
                    wall_times.append(wall)
                    cpu_times.append(cpu)
                    mems.append(mem)
                progress.advance(task)

            if verbose and errors:
                typer.echo(f"[{bench.name}] Errors: {errors}")

            if not wall_times:
                raise typer.Exit(f"[{bench.name}] All iterations failed: {errors}")

            result = {
                "wall_time": compute_stats(wall_times),
                "cpu_time": compute_stats(cpu_times),
                "peak_memory": compute_stats(mems),
            }
            results[bench.name] = result

    return results