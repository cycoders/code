import json
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import console
from rich.progress import Progress
from jsonschema import RefResolver

from .generator import generate_fixture, inline_schema
from .parsers import get_schema_dict

app = typer.Typer(no_args_is_help=True)
c = console.Console()

@app.command()
def gen(
    schema_file: Path = typer.Argument(..., help="JSON Schema or OpenAPI file (JSON/YAML)"),
    pydantic_module: Optional[Path] = typer.Option(None, "--pydantic-module", help="Path to Python file with Pydantic model"),
    pydantic_model: str = typer.Option("", "--model", help="Pydantic model name (e.g. User)"),
    component: Optional[str] = typer.Option(None, "--component", help="OpenAPI component schema name"),
    count: int = typer.Option(5, "--count/-n", min=1, max=10000),
    seed: Optional[int] = typer.Option(None, "--seed"),
    output_file: Optional[Path] = typer.Option(None, "--output/-o", help="Output file (default: stdout)"),
    fmt: str = typer.Option("json", "--format/-f", help="json | yaml | ndjson"),
    preview: bool = typer.Option(False, "--preview"),
):
    """Generate schema-compliant test fixtures."""
    try:
        schema_dict = get_schema_dict(
            schema_file, pydantic_module, pydantic_model, component
        )
    except Exception as e:
        typer.echo(f"[red]Error loading schema: {e}[/red]", err=True)
        raise typer.Exit(code=1)

    resolver = RefResolver(base_uri="#", referrer=schema_dict)
    schema_inlined = inline_schema(schema_dict, resolver)

    faker_instance = Faker(seed=seed)

    if preview:
        fixture = generate_fixture(schema_inlined, faker_instance)
        c.print_json(data=fixture, indent=2)
        return

    with Progress() as progress:
        task = progress.add_task("[green]Generating fixtures...", total=count)
        fixtures = []
        for _ in range(count):
            fixtures.append(generate_fixture(schema_inlined, faker_instance))
            progress.advance(task)

    output_str = format_output(fixtures, fmt)

    if output_file:
        output_file.write_text(output_str, encoding="utf-8")
        c.print(f"[green]Wrote {count} fixtures to [blue]{output_file}[/blue].[/green]")
    else:
        print(output_str)


def format_output(fixtures: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(fixtures, indent=2, ensure_ascii=False)
    elif fmt == "yaml":
        return yaml.dump(fixtures, default_flow_style=False, allow_unicode=True)
    elif fmt == "ndjson":
        return "\n".join(json.dumps(f, separators=(',', ':'), ensure_ascii=False) for f in fixtures) + "\n"
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def main():
    app()


if __name__ == "__main__":
    main()
