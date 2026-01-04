import json
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.json import JSON
import jsonschema
from .infer import infer_schema


app = typer.Typer()
console = Console()


@app.command()
def infer(
    files: List[typer.FileText],
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    confidence: float = typer.Option(0.9, "-c", "--confidence", min=0.0, max=1.0),
) -> None:
    """Infer schema from JSON samples."""
    try:
        samples = [json.loads(f.read()) for f in files]
        schema = infer_schema(samples, confidence)

        if output:
            output.write_text(json.dumps(schema, indent=2, ensure_ascii=False))
            typer.echo(f"Schema saved to {output}")
        else:
            console.print(JSON(schema, indent="  "))
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Inference failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    schema_file: Path = typer.Argument(..., help="Schema file"),
    data_files: List[Path] = typer.Argument(..., help="JSON data files"),
) -> None:
    """Validate JSON files against schema."""
    try:
        with schema_file.open("r") as f:
            schema = json.load(f)
        for data_file in data_files:
            with data_file.open("r") as f:
                data = json.load(f)
            try:
                jsonschema.validate(instance=data, schema=schema)
                typer.echo(f"✓ {data_file.name}")
            except jsonschema.ValidationError as e:
                typer.echo(f"✗ {data_file.name}: {e.message}", err=True)
    except Exception as e:
        typer.echo(f"Validation failed: {e}", err=True)
        raise typer.Exit(1)


def main() -> int:
    app(prog_name="json-schema-inferrer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
