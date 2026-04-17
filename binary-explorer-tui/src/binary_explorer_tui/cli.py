import typer
from pathlib import Path
import sys
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .analyzer import BinaryAnalyzer
from .tui_app import BinaryExplorerApp

from textual import run_app


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()


def _print_table(title: str, headers: list[str], rows: list):
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for h in headers:
        table.add_column(h, style="cyan")
    for row in rows:
        table.add_row(*[str(x) for x in row])
    console.print(table)


def _handle_error(path: Path):
    rprint(Panel.fit(f"[red bold]Error:[/red bold] Cannot parse '{path}'. Ensure it's a valid ELF/PE/Mach-O binary.", border_style="red"))
    raise typer.Exit(1)


@app.command(help="Show basic binary info")
def info(path: Path):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    info_rows = [
        ["Format", analyzer.format],
        ["Architecture", analyzer.architecture],
        ["Entry Point", f"0x{analyzer.entrypoint:x}"],
        ["File Size", analyzer.file_size_human],
    ]
    _print_table("Binary Info", ["Property", "Value"], info_rows)


@app.command(help="List dynamic dependencies")
def deps(path: Path):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    _print_table("Dependencies", ["Library"], [[lib] for lib in analyzer.libraries])


@app.command(help="Show sections with entropy")
def sections(path: Path):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    headers = ["Name", "VA", "Size", "Entropy"]
    rows = []
    for sec in analyzer.sections:
        va_str = f"0x{sec['va']:x}" if sec["va"] is not None else "N/A"
        rows.append([sec["name"], va_str, sec["size_human"], f"{sec['entropy']:.2f}"])
    _print_table("Sections", headers, rows)


@app.command(help="List symbols")
def symbols(path: Path, limit: int = typer.Option(100, "--limit")):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    headers = ["Name", "Value", "Size"]
    rows = analyzer.symbol_rows[:limit]
    _print_table(f"Symbols (top {limit})", headers, rows)


@app.command(help="List strings (min len 5, top 100)")
def strings(path: Path, min_len: int = 5, limit: int = typer.Option(100, "--limit")):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    _print_table(f"Strings (len>={min_len}, top {limit})", ["String"], [[s] for s in analyzer.strings[:limit]])


@app.command(help="Launch interactive TUI")
def tui(path: Path):
    try:
        analyzer = BinaryAnalyzer(path)
    except ValueError:
        _handle_error(path)

    try:
        run_app(BinaryExplorerApp(analyzer))
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        rprint(f"[red]TUI error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
