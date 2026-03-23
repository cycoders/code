import typer
import os
import glob
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

import route_extractor_cli.models as models
from route_extractor_cli.extractors import get_extractor
from route_extractor_cli.utils import parse_path_params, generate_openapi

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command(help="Extract routes from a Python project")
def extract(
    path: Path = typer.Argument(Path("."), help="Project path to scan"),
    framework: str = typer.Option("auto", "--framework", help="fastapi|flask|django|auto"),
    output: str = typer.Option("table", "--output", help="table|json|markdown"),
    export_openapi: Optional[Path] = typer.Option(None, "--export-openapi", help="Export OpenAPI spec"),
):
    """Extract and display routes."""
    if not path.exists():
        typer.echo("❌ Path does not exist.", err=True)
        raise typer.Exit(1)

    py_files = list(path.rglob("*.py"))
    if not py_files:
        typer.echo("❌ No Python files found.", err=True)
        raise typer.Exit(1)

    with Progress() as progress:
        task = progress.add_task("[green]Parsing...", total=len(py_files))
        routes: List[models.Route] = []
        extractor_cls = get_extractor(framework)
        extractor = extractor_cls()

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = compile(content, str(py_file), "exec", flags=0)
                import ast
                ast_tree = ast.parse(content, str(py_file))
                extractor.visit(ast_tree)
            except SyntaxError:
                pass  # Skip invalid
            progress.advance(task)

        routes = extractor.routes

    if not routes:
        typer.echo("❌ No routes found. Check framework or code.")
        raise typer.Exit(1)

    if output == "table":
        table = Table(title=f"API Routes ({len(routes)} found, {framework or 'auto'}) ")
        table.add_column("Method", style="cyan")
        table.add_column("Path", style="magenta")
        table.add_column("Handler")
        table.add_column("Parameters", max_width=40)
        for route in routes:
            params_str = ", ".join(
                f"{p.name}:{p.type_hint or 'str'}{'?' if not p.required else ''}" for p in route.parameters
            ) or "-"
            methods = ", ".join(route.methods)
            table.add_row(methods, route.path, route.handler, params_str)
        console.print(table)

    elif output == "json":
        console.print(models.Route.schema_json_(routes, indent=2))

    elif output == "markdown":
        md = "| Method | Path | Handler | Parameters |\n|--------|------|---------|------------|\n"
        for route in routes:
            params_str = ", ".join(f"{p.name}:{p.type_hint or 'str'}" for p in route.parameters)
            md += f"| {', '.join(route.methods)} | {route.path} | {route.handler} | {params_str or '-'} |\n"
        console.print(md)

    if export_openapi:
        openapi_spec = generate_openapi(routes)
        export_openapi.write_text(openapi_spec.model_dump_json(indent=2))
        typer.echo(f"📄 OpenAPI spec exported to {export_openapi}")

    typer.echo(f"✅ Extracted {len(routes)} routes from {len(py_files)} files.")

if __name__ == "__main__":
    app()
