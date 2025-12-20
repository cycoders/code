import typer
from pathlib import Path
from rich.console import Console
from .profiler import monitor_script
from .reporter import report_session

app = typer.Typer(help="Detect Python memory leaks via RSS and tracemalloc.")

@app.command()
def monitor(
    script: Path = typer.Argument(..., help="Python script to profile"),
    *,
    args: list[str] = typer.Argument([], help="Script args"),
    duration: float = typer.Option(60.0, "-d", "--duration", min=0, help="Max seconds (0=Ctrl+C)"),
    interval: float = typer.Option(5.0, "-i", "--interval", min=0.1, help="Poll interval (s)"),
    rss_threshold_mb: float = typer.Option(50.0, "-r", "--rss-threshold", min=0, help="RSS delta threshold (MB)"),
    heap_threshold_bytes: int = typer.Option(1_048_576, "-h", "--heap-threshold", min=0, help="Min leak size per diff (bytes)"),
    output: Path = typer.Option(None, "-o", "--output", help="Save session dir"),
):
    """Monitor script for leaks."""
    console = Console()
    monitor_script(
        console,
        script,
        args,
        duration,
        interval,
        rss_threshold_mb * 1024**2,
        heap_threshold_bytes,
        output,
    )

@app.command()
def report(session_dir: Path = typer.Argument(..., help="Session directory")):
    """Report on saved session."""
    console = Console()
    report_session(console, session_dir)
