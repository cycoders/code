from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console

from exception_graph_cli.analyzer import find_python_files, extract_exceptions
from exception_graph_cli.graph import build_graph
from exception_graph_cli.renderers import to_mermaid

app = typer.Typer(help="Build exception propagation graphs")
console = Console()


@app.command()
def main(
    path: Path = typer.Argument(..., exists=True, file_okay=False),
    format: str = typer.Option("mermaid", "--format", "-f"),
    out: Path | None = typer.Option(None, "--out", "-o"),
):
    """Generate exception graph for a Python package."""
    files = list(find_python_files(path, {"venv", "__pycache__"}))
    g = build_graph(files)
    if format == "mermaid":
        result = to_mermaid(g)
    else:
        result = str(g)
    if out:
        out.write_text(result)
    else:
        console.print(result)
