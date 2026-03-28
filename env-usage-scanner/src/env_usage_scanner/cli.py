import typer
from pathlib import Path
from typing import List, Optional

import env_usage_scanner.models as models
import env_usage_scanner.scanner as scanner
import env_usage_scanner.output as output


app = typer.Typer(add_completion=False)


@app.command(help="Scan directory for env var usages")
def scan(
    path: Path = typer.Argument(Path("."), exists=True),
    langs: List[str] = typer.Option([], "--lang", help="Filter languages (python,js,go,...)"),
    exclude: List[str] = typer.Option([], "--exclude"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Scan codebase for env var usages."""
    usages = scanner.scan_directory(path, langs, exclude)

    if json:
        output.output_json(usages)
    else:
        output.print_scan_results(usages)


@app.command(help="Generate .env template")
def template(
    path: Path = typer.Argument(Path("."), exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    langs: List[str] = typer.Option([], "--lang"),
    exclude: List[str] = typer.Option([], "--exclude"),
):
    usages = scanner.scan_directory(path, langs, exclude)
    output.generate_template(usages, output)


@app.command(help="Detect unused/missing vars vs .env")
def unused(
    path: Path = typer.Argument(Path("."), exists=True),
    env_file: Path = typer.Argument(..., help="Path to .env"),
    langs: List[str] = typer.Option([], "--lang"),
    exclude: List[str] = typer.Option([], "--exclude"),
):
    if not env_file.exists():
        typer.echo(f"[red]Env file not found: {env_file}[/red]", err=True)
        raise typer.Exit(1)

    usages = scanner.scan_directory(path, langs, exclude)
    used = set(usages.keys())
    defined = scanner.parse_env_file(env_file)

    output.print_unused(defined, used)


@app.command(help="Generate Mermaid usage graph")
def graph(
    path: Path = typer.Argument(Path("."), exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output .mmd file"),
    langs: List[str] = typer.Option([], "--lang"),
    exclude: List[str] = typer.Option([], "--exclude"),
):
    usages = scanner.scan_directory(path, langs, exclude)
    output.generate_mermaid_graph(usages, output)


if __name__ == "__main__":
    app()
