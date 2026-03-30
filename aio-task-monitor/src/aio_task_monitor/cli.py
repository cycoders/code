import typer
import sys
from rich.console import Console
from rich.table import Table
from aio_task_monitor.snapshot import take_snapshot

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()


@app.command()
def monitor():
    """
    Start the interactive TUI monitor (blocks until quit).
    """
    from .tui.app import MonitorApp

    MonitorApp().run()


@app.command()
def snapshot(fmt: str = "table"):
    """
    Print a one-shot snapshot of current tasks.

    FMT: 'table' (rich table) or 'json'.
    """
    data = take_snapshot()

    if fmt == "json":
        import json
        print(json.dumps(data, indent=2, default=str))
        raise typer.Exit()

    # Table
    table = Table(title="Asyncio Tasks Snapshot", show_header=True, box=None)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Coro", style="green")
    table.add_column("Done", justify="center")
    table.add_column("Cancelled", justify="center")

    for task in data["tasks"]:
        table.add_row(
            str(task["task_id"]),
            task["name"],
            task["coro_name"],
            "✓" if task["done"] else "✗",
            "✗" if task["cancelled"] else " ",
        )

    console.print(table)
    console.print(f"\nStats: {data['stats']}")


if __name__ == "__main__":
    app()


def main(standalone_mode: bool = True):
    if standalone_mode:
        app()
    else:
        # Called from __init__.py thread
        monitor()
