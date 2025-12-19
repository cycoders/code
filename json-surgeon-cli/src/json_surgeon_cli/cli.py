import typer
from pathlib import Path
from typing import Optional

from .app import JsonSurgeonApp

cli = typer.Typer(name="json-surgeon-cli", add_completion=False)

@cli.command(help="Launch interactive JSON TUI")
def main(
    json_file: Optional[Path] = typer.Argument(None, help="JSON file path (or pipe from stdin)"),
):
    """
    Interactive JSON surgeon.

    Examples::

        json-surgeon-cli data.json
        curl api | json-surgeon-cli
    """
    app = JsonSurgeonApp(str(json_file) if json_file else None)
    app.run()

if __name__ == "__main__":
    cli()