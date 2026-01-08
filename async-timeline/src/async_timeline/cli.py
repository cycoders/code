import sys
import asyncio
import runpy
import typer
from pathlib import Path
from typing import List

from rich.console import Console
from rich.traceback import install

install(show_locals=True)

from .profiler import AsyncProfiler
from .reporter import generate_report

app = typer.Typer()
console = Console()

@app.command(help="Instrument and visualize an asyncio script")
def run(
    script: Path = typer.Argument(..., exists=True, help="Async Python script to profile"),
    extra_args: List[str] = typer.Argument([], help="Arguments to pass to the script"),
    poll_interval: float = typer.Option(0.01, "--poll-interval", min=0.001, help="Concurrency sampler interval (s)"),
):
    """Run script with instrumentation."""
    # Setup argv for script
    orig_argv = sys.argv[:]
    sys.argv = [script.name] + extra_args

    profiler = AsyncProfiler(poll_interval)

    try:
        profiler.start()
        runpy.run_path(
            script,
            run_name="__main__",
            globals={"__name__": "__main__", "__file__": str(script)},
        )
        profiler.stop()
    except KeyboardInterrupt:
        typer.echo("[yellow]Interrupted[/yellow]")
        profiler.stop()
    except Exception:
        profiler.stop()
        raise
    finally:
        sys.argv = orig_argv  # Restore

    if not profiler.tasks:
        console.print("[red]No asyncio tasks detected. Use asyncio.create_task() or gather().[/]")
        raise typer.Exit(1)

    generate_report(profiler, console)


if __name__ == "__main__":
    app()