import typer
import sys
from pathlib import Path
from typing import List, Dict, Any

from avro_schema_diff_cli import __version__
from avro_schema_diff_cli.utils import load_schema, get_schemas, validate_schema
from avro_schema_diff_cli.differ import get_schema_diff
from avro_schema_diff_cli.renderer import render_results
from rich.console import Console
from rich.traceback import install


app = typer.Typer(no_args_is_help=True)
console = Console()
install(show_locals=True)


@app.command()
def version():
    typer.echo(f"avro-schema-diff-cli {__version__}")


@app.command()
def diff(
    old: Path = typer.Argument(..., help="Old schema file/dir"),
    new: Path = typer.Argument(..., help="New schema file/dir"),
    output: str = typer.Option("rich", "--output", "-o", help="Output: rich|json|text"),
    check_backward: bool = typer.Option(False, "--check-backward", help="Fail if not backward compat"),
    check_forward: bool = typer.Option(False, "--check-forward", help="Fail if not forward compat"),
    exit_breaking: bool = typer.Option(False, "--exit-on-breaking", help="Exit 1 if breaking"),
):
    """Diff Avro schemas and check compatibility."""
    try:
        if old.is_dir():
            old_schemas = get_schemas(old)
            new_dir = new if new.is_dir() else typer.Abort("New must be dir if old is dir")
        else:
            old_schemas = [load_schema(old)]
            new_dir = Path(".")
        results: List[Dict[str, Any]] = []
        for oschema in old_schemas:
            validate_schema(oschema)
            name = oschema.get("name", "unnamed")
            npath = new_dir / f"{name}.avsc" if new_dir.is_dir() else new
            if not npath.exists():
                console.print(f"[yellow]No matching new schema for {name}[/yellow]")
                continue
            nschema = load_schema(npath)
            validate_schema(nschema)
            changes = get_schema_diff(oschema, nschema, name)
            results.append({"name": name, "changes": changes})
        render_results(results, output, console)
        breaking = any(
            not (r["changes"].get("backward_compatible", True) and r["changes"].get("forward_compatible", True))
            for r in results
        )
        if exit_breaking and breaking:
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app(prog_name="avro-schema-diff")
