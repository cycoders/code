import typer
from pathlib import Path
from typing import Optional, Union

from rich.console import Console

from .detector import detect_lockfile
from .parsers import parse_graph
from .tree_builder import build_forest
from .renderer import render, RenderError

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command()
def viz(
    path: Path = typer.Argument(Path("."), help="Path to project directory"),
    format_: str = typer.Option("ascii", "--format", "-f", help="Output format (ascii, mermaid, png, svg)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path (stdout if omitted)"),
    max_depth: int = typer.Option(10, "--max-depth", "-d", min=1, max=50, help="Maximum tree depth"),
    include_dev: bool = typer.Option(False, "--include-dev/--no-dev", help="Include dev dependencies"),
):
    """
    Visualize dependency tree from lockfiles.
    """
    project_path = path.resolve()
    lock_info = detect_lockfile(project_path)

    if not lock_info:
        typer.echo("❌ No supported lockfile found (Poetry.lock, package-lock.json, Cargo.lock).", err=True)
        raise typer.Exit(code=1)

    parser_type, lock_path, manifest_path = lock_info
    typer.echo(f"🔍 Detected {parser_type} lockfile: {lock_path.name}")

    try:
        roots, graph = parse_graph(parser_type, project_path, lock_path, manifest_path, include_dev)
        if not roots:
            typer.echo("⚠️  No root dependencies found.")
            raise typer.Exit(code=1)
        typer.echo(f"📊 {len(roots)} roots, {len(graph)} total packages.")

        forest = build_forest(roots, graph, max_depth)
        result = render(forest, format_)

        if isinstance(result, bytes):
            if not output:
                typer.echo("❌ --output required for binary formats (png/svg).", err=True)
                raise typer.Exit(code=1)
            output.write_bytes(result)
            typer.echo(f"💾 PNG/SVG exported to {output}")
        else:
            if output:
                output.write_text(result)
                typer.echo(f"💾 Text exported to {output}")
            else:
                console.print(result)

    except RenderError as e:
        typer.echo(f"❌ Render error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"💥 Parse error: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()