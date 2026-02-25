import subprocess
import time
from typing import Dict, Tuple

from rich.progress import Progress


def test_connectivity(host: str, config_path: str, timeout: int = 5) -> Tuple[bool, float]:
    """Test SSH connectivity to host using config."""
    start = time.time()
    try:
        cmd = [
            "ssh",
            "-F", config_path,
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", f"ConnectTimeout={timeout}",
            host,
            "-O", "check",
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=timeout + 2)
        return True, time.time() - start
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False, time.time() - start


def batch_test_connectivity(
    hosts: list[str], config_path: str, timeout: int = 5
) -> Dict[str, Tuple[bool, float]]:
    """Batch test with progress."""
    results = {}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as progress:
        task = progress.add_task("Testing hosts...", total=len(hosts))
        for host in hosts:
            results[host] = test_connectivity(host, config_path, timeout)
            progress.advance(task)
    return results