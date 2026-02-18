import shlex
import sys
import typer
from typing import List

from .benchmark import benchmark_commands
from .reporter import print_results


app = typer.Typer(add_completion=False, invoke_without_command=True)


@app.command()
def run(
    commands: List[str] = typer.Argument(
        ..., help="One or more commands to benchmark (quote if args contain spaces, e.g. \"git status\")"
    ),
    warmup_runs: int = typer.Option(3, "--warmup/-w", min=0, help="Warmup runs (discarded)"),
    num_runs: int = typer.Option(30, "--runs/-n", min=1, help="Benchmark runs per command"),
    timeout: float = typer.Option(10.0, "--timeout/-t", min=0.1, help="Timeout per run (s)"),
    json_output: bool = typer.Option(False, "--json/-j", help="JSON output"),
    verbose: bool = typer.Option(False, "--verbose/-v", help="Show stdout/stderr on failure"),
) -> None:
    """Benchmark CLI commands with comprehensive metrics."""
    benchmarked = []
    for cmd_str in commands:
        cmd = shlex.split(cmd_str)
        typer.echo(f"[bold cyan]Benchmarking:[/bold cyan] {' '.join(cmd)}")
        results = benchmark_commands(cmd, warmup_runs, num_runs, timeout, verbose)
        benchmarked.append({"command": cmd_str, "results": results})

    if json_output:
        import json
        print(json.dumps(benchmarked, indent=2), file=sys.stdout)
    else:
        print_results(benchmarked)


if __name__ == "__main__":  # pragma: no cover
    app()