import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console

console = Console()

def run_task(cmd: str) -> int:
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        console.print(f"[red]Failed:[/red] {cmd}")
    return proc.returncode