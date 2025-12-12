import sys
import typer
from pathlib import Path
from typing import List

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import load_config
from .runner import run_experiments
from .analyzer import analyze_reports
from .reporter import report_console, report_json, report_html

cli = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)

@cli.command()
def detect(
    num_runs: int = typer.Option(10, "--num-runs", "-n", min=1, show_default=True),
    threshold: float = typer.Option(0.05, "--threshold", "-t", min=0.0, max=1.0, show_default=True),
    pytest_args: List[str] = typer.Option([], "--pytest-args"),
    config: Path = typer.Option(None, "--config", "-c"),
    output_dir: str = typer.Option("flake-reports", "--output", "-o", show_default=True),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Detect flaky tests by running pytest multiple times."""

    cfg: dict = {}
    if config and config.exists():
        cfg = load_config(config)
        num_runs = cfg.get("num_runs", num_runs)
        threshold = cfg.get("threshold", threshold)
        pytest_args = cfg.get("pytest_args", []) + pytest_args
        output_dir = cfg.get("output_dir", output_dir)

    output_path = Path(output_dir)
    if output_path.exists() and not force:
        console.print("[yellow]Output dir exists. Use --force to overwrite.")
        raise typer.Exit(code=1)
    output_path.mkdir(exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running pytest experiments...", total=num_runs)
        run_experiments(num_runs, pytest_args, output_path, progress, task)

    reports_path = output_path / "reports"
    reports_path.mkdir(exist_ok=True)

    stats = analyze_reports(output_path)
    flaky = [s for s in stats if s["flake_rate"] > threshold]

    rprint(Panel.fit(
        f"[bold green]Flaky tests (>{threshold*100:.1f}% fail rate): {len(flaky)}",
        title="[bold]Summary",
        style="green",
    ))

    report_console(stats, threshold, console)
    report_json(stats, reports_path / "stats.json")
    report_html(stats, threshold, reports_path / "report.html")

    console.print(f"[dim]Reports in: {reports_path}")

    if flaky:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()