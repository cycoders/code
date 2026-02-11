import typer
from pathlib import Path
from typing import Annotated

import rich.console

from . import __version__
from .generator import collect_components
from .formatter import FORMATTERS


app = typer.Typer(no_args_is_help=True, add_completion=False)
console = rich.console.Console()


@app.command(help="Show dependency table preview")
def table(path: Annotated[Path, typer.Argument(path_type=Path, exists=True, resolve_path=True)] = typer.Argument(Path("."))):
    """Preview dependencies in rich table."""
    components = collect_components(path)

    from rich.table import Table

    table = Table(title="Dependencies", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("PURL", style="dim")

    for c in components[:50]:  # Top 50
        table.add_row(c.name, c.version, c.purl)
    if len(components) > 50:
        table.add_row("...", f"+{len(components)-50} more", "")

    console.print(table)


@app.command(help="Detect package managers")
def detect(path: Annotated[Path, typer.Argument(path_type=Path, exists=True)] = typer.Argument(Path("."))):
    """List detected package managers."""
    from .detector import DetectorRegistry

    reg = DetectorRegistry(path)
    active = reg.get_active()
    names = [d.__class__.__name__.replace("Detector", "").lower() for d in active]
    console.print(f"Detected: {', '.join(names) or 'none'}")


@app.command(help="Generate SBOM")
def generate(
    path: Annotated[Path, typer.Argument(path_type=Path, exists=True)] = typer.Argument(Path(".")),
    fmt: Annotated[str, typer.Option("cyclonedx", "--format", "-f", case_insensitive=True, show_default=True)] = "cyclonedx",
    output: Annotated[str, typer.Option("-", "--output", "-o", show_default=True)] = "-",
):
    """Generate SBOM file."""
    if fmt not in FORMATTERS:
        raise typer.BadParameter(f"Format must be {list(FORMATTERS)}")

    components = collect_components(path)
    bom_str = FORMATTERS[fmt](components, {"project": path.name})

    if output == "-":
        print(bom_str)
    else:
        out_path = Path(output)
        out_path.write_text(bom_str, encoding="utf-8")
        console.print(f"[green]Wrote[/green] SBOM to [blue]{out_path}[/blue]")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version", show_default=False),
):
    """Lightweight SBOM generator for dev supply chain security."""
    if version:
        console.print(f"sbom-generator-cli {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()