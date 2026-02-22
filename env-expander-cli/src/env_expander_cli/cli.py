import typer
from pathlib import Path
from typing import Optional

from .expander import EnvExpander
from .expander_errors import ExpansionError
from .utils import load_env, dump_env
from .validator import load_schema, validate_env
from .differ import print_env_diff


app = typer.Typer(
    help="Expand interpolated .env files with validation & diffs.",
    invoke_without_command=True,
)


@app.command()
def expand(
    file: Path = typer.Argument(Path(".env"), help="Input .env"),
    output: Path = typer.Argument(..., help="Output file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview expansions"),
):
    """Expand interpolated vars to output file."""
    try:
        env = load_env(file)
        expander = EnvExpander(env)
        expanded = expander.expand_all()
        if dry_run:
            typer.echo("[bold green]Expanded:[/]")
            for k, v in sorted(expanded.items()):
                typer.echo(f"  {k}: {v}")
            return
        json_out = output.suffix.lower() == ".json"
        dump_env(expanded, output, json_out)
        typer.echo(f"[bold green]✓[/] Wrote to {output} {'(JSON)' if json_out else '(ENV)'}")
    except (FileNotFoundError, ExpansionError) as e:
        typer.echo(f"[bold red]✗[/] {e}", err=True)
        raise typer.Exit(1)


@app.command()
def lint(
    file: Path = typer.Argument(Path(".env")),
    schema: Optional[Path] = typer.Option(None, "--schema", help="YAML schema"),
):
    """Lint: expand, check cycles, validate schema."""
    try:
        env = load_env(file)
        expander = EnvExpander(env)
        expanded = expander.expand_all()
        typer.echo("[bold green]✓[/] Expansion OK (no cycles)")
        if schema:
            sch = load_schema(schema)
            errors = validate_env(expanded, sch)
            if errors:
                for err in errors:
                    typer.echo(f"[bold red]✗[/] {err}")
                raise typer.Exit(1)
            typer.echo("[bold green]✓[/] Schema validation passed")
    except (FileNotFoundError, ExpansionError) as e:
        typer.echo(f"[bold red]✗[/] {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    file: Path = typer.Argument(Path(".env")),
    schema: Path = typer.Option(..., "--schema"),
):
    """Validate expanded env against schema (expands first)."""
    env = load_env(file)
    expander = EnvExpander(env)
    expanded = expander.expand_all()
    sch = load_schema(schema)
    errors = validate_env(expanded, sch)
    if errors:
        for err in errors:
            typer.echo(f"[bold red]✗[/] {err}")
        raise typer.Exit(1)
    typer.echo("[bold green]✓[/] All good!")


@app.command()
def diff(file1: Path, file2: Path):
    """Pretty diff of two expanded .env files."""
    try:
        env1 = load_env(file1)
        env2 = load_env(file2)
        expander1 = EnvExpander(env1)
        expanded1 = expander1.expand_all()
        expander2 = EnvExpander(env2)
        expanded2 = expander2.expand_all()
        console = typer.console
        print_env_diff(expanded1, expanded2, console)
    except (FileNotFoundError, ExpansionError) as e:
        typer.echo(f"[bold red]✗[/] {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()