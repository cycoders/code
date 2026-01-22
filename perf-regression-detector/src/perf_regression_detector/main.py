import sys
import typer
from pathlib import Path
from typing import Optional

from rich.console import Console

from .config import load_config, Benchmark
from .measure import run_benchmarks
from .baseline import load_baseline, save_baseline, update_baseline_file
from .reporter import report_results


cli = typer.Typer(no_args_is_help=True)
console = Console()


@cli.command(help="Initialize perf-regression.yaml config")
def init(
    config: Path = typer.Option(Path("perf-regression.yaml"), "--config", "-c"),
):
    if config.exists():
        console.print(f"[yellow]{config} exists, skipping.[/yellow]")
        return
    example = """benchmarks:
  - name: example
    command: python
    args: ['-c', 'import time; time.sleep(0.01)']
    iterations: 50
    timeout: 30.0
    metrics: [wall_time, cpu_time, peak_memory]
"""
    config.write_text(example)
    console.print(f"[green]Created {config}. Edit and commit![/green]")


@cli.command(help="Run benchmarks and show results (no baseline check)")
def run(
    threshold: float = typer.Option(5.0, "--threshold/-t"),
    config: Path = typer.Option(Path("perf-regression.yaml"), "--config/-c"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    benchmarks = load_config(config)
    results = run_benchmarks(benchmarks, verbose=verbose)
    base_results = None
    report_results(results, base_results, threshold)


@cli.command(help="Check current vs baseline, exit 1 on regression")
def check(
    threshold: float = typer.Option(5.0, "--threshold/-t"),
    baseline_ref: Optional[str] = typer.Option(None, "--baseline"),
    config: Path = typer.Option(Path("perf-regression.yaml"), "--config/-c"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    benchmarks = load_config(config)
    results = run_benchmarks(benchmarks, verbose=verbose)
    base_results = load_baseline(baseline_ref) if baseline_ref else None
    report_results(results, base_results, threshold, fail_on_regression=True)


@cli.command(help="Run benchmarks and RECORD/UPDATE baseline.json")
def record(
    commit: bool = typer.Option(False, "--commit"),
    config: Path = typer.Option(Path("perf-regression.yaml"), "--config/-c"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    benchmarks = load_config(config)
    results = run_benchmarks(benchmarks, verbose=verbose)
    baseline_path = Path(".perf-regression/baseline.json")
    save_baseline(results, baseline_path)
    console.print(f"[green]Saved baseline to {baseline_path}[/green]")
    if commit:
        import subprocess
        subprocess.run(["git", "add", str(baseline_path)], check=True)
        subprocess.run(
            ["git", "commit", "-m", "perf(baseline): update benchmarks"], check=True
        )
        console.print("[green]Committed baseline.json[/green]")


@cli.command(help="Show current baseline.json")
def baseline(
    ref: Optional[str] = typer.Option(None, "--ref"),
    config: Path = typer.Option(Path("perf-regression.yaml"), "--config/-c"),
):
    base_results = load_baseline(ref)
    if not base_results:
        console.print("[yellow]No baseline found.[/yellow]")
        raise typer.Exit(1)
    benchmarks = load_config(config)
    # Fake current as None
    report_results(None, base_results, 0)


if __name__ == "__main__":
    cli()