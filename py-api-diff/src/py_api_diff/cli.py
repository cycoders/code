import typer
from pathlib import Path
from typing import Optional

import rich.console

from . import parser
from .differ import diff
from .reporter import report


app = typer.Typer(help="Detect Python API breaking changes.")


@app.command()
def main(
    old: str = typer.Argument("main", help="Old git rev"),
    new: str = typer.Argument("HEAD", help="New git rev"),
    root: Optional[Path] = typer.Option(None, "--root", help="Git root (auto-detect)"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    no_color: bool = typer.Option(False, "--no-color"),
):
    """Detect breaking API changes OLD -> NEW."""
    console = rich.console.Console(color_system="standard" if not no_color else None, no_color=no_color)

    root_path = root or parser.get_git_root()
    console.print(f"[blue]🔍 Diffing {old} -> {new} in [bold]{root_path}[/][blue]...[/]\n")

    old_apis = parser.parse_tree(root_path, old)
    new_apis = parser.parse_tree(root_path, new)

    result = diff(old_apis, new_apis)
    report(console, result, verbose)


if __name__ == "__main__":
    app()