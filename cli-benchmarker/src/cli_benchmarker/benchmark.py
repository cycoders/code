import subprocess
import sys
import threading
import time
from typing import Any, Dict, List

import psutil


def benchmark_commands(
    cmd: List[str],
    warmup_runs: int,
    num_runs: int,
    timeout: float,
    verbose: bool,
) -> List[Dict[str, Any]]:
    """Run warmup then benchmark runs."""
    # Warmup (discarded)
    for _ in range(warmup_runs):
        run_once(cmd, timeout, verbose)

    # Benchmark
    results = []
    for _ in range(num_runs):
        result = run_once(cmd, timeout, verbose)
        results.append(result)
    return results


def run_once(cmd: List[str], timeout: float, verbose: bool) -> Dict[str, Any]:
    """Run command once, capture metrics."""
    start_wall = time.monotonic()
    proc: subprocess.Popen | None = None
    peak_mem_mb = 0.0

    def monitor_memory() -> None:
        nonlocal peak_mem_mb
        while proc and proc.poll() is None:
            try:
                mem_mb = psutil.Process(proc.pid).memory_info().rss / (1024 * 1024)
                peak_mem_mb = max(peak_mem_mb, mem_mb)
                time.sleep(0.02)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                break

    mem_thread = threading.Thread(target=monitor_memory, daemon=True)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            text=False,
            close_fds=True,
        )
        mem_thread.start()
        stdout, stderr = proc.communicate(timeout=timeout)
        wall_time = time.monotonic() - start_wall
        exit_code = proc.returncode

        # CPU times
        try:
            ct = psutil.Process(proc.pid).cpu_times()
            cpu_user = ct.user + getattr(ct, "children_user", 0.0)
            cpu_sys = ct.system + getattr(ct, "children_system", 0.0)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            cpu_user = cpu_sys = 0.0

        if verbose and exit_code != 0:
            if stdout:
                sys.stderr.buffer.write(stdout)
                sys.stderr.write("\n")
            if stderr:
                sys.stderr.buffer.write(stderr)
                sys.stderr.write("\n")

        return {
            "wall_time": wall_time,
            "cpu_user": cpu_user,
            "cpu_sys": cpu_sys,
            "cpu_total": cpu_user + cpu_sys,
            "mem_peak_mb": peak_mem_mb,
            "exit_code": exit_code,
            "success": exit_code == 0,
        }

    except subprocess.TimeoutExpired:
        if proc:
            proc.kill()
            proc.communicate()
        sys.stderr.write(f"[red]Timeout ({timeout}s)[/red]\n")
        return {
            "wall_time": timeout,
            "cpu_user": 0.0,
            "cpu_sys": 0.0,
            "cpu_total": 0.0,
            "mem_peak_mb": peak_mem_mb,
            "exit_code": -9,
            "success": False,
        }