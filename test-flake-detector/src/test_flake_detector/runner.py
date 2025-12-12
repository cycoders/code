import subprocess
import typer
from pathlib import Path
from typing import List, Any

def run_experiments(
    num_runs: int,
    pytest_args: List[str],
    output_path: Path,
    progress: Any,
    task_id: Any,
) -> None:
    """Run pytest N times, save stdout to files."""
    output_path.mkdir(exist_ok=True)

    for i in range(num_runs):
        stdout_file = output_path / f"run_{i+1:03d}.txt"
        err_file = output_path / f"run_{i+1:03d}_err.txt"
        cmd = ["pytest", "-v", "--tb=no"] + pytest_args

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
                check=False,
            )
            stdout_file.write_text(result.stdout)
            if result.stderr.strip():
                err_file.write_text(result.stderr)
            if result.returncode not in (0, 5):  # 5: no tests collected
                typer.secho(f"Run {i+1}: exit {result.returncode}", fg="yellow")
        except subprocess.TimeoutExpired:
            typer.secho(f"Run {i+1}: timeout", fg="red")
            stdout_file.write_text("TIMEOUT")

        progress.advance(task_id)