import sys
import pathlib
from typing import Annotated

import typer
from rich.console import Console

import sql_index_suggester
from .query_analyzer import analyze_queries
from .index_suggester import generate_suggestions
from .renderer import render_table, render_json
from .schema import extract_schema


app = typer.Typer()
console = Console()


@app.command()
def suggest(
    schema_file: Annotated[pathlib.Path, typer.Argument(..., help="Schema DDL SQL")],
    queries_file: Annotated[pathlib.Path, typer.Argument(..., help="Queries SQL")],
    dialect: str = typer.Option("postgres", "--dialect", help="SQL dialect"),
    output: str = typer.Option("table", "--output/-o", help="table|json"),
    min_score: float = typer.Option(20.0, "--min-score", help="Minimum suggestion score"),
) -> None:
    try:
        schema_sql = schema_file.read_text()
        queries_sql = queries_file.read_text()

        schema = extract_schema(schema_sql, dialect)
        if not schema.tables:
            console.print("[red]No tables found in schema.[/]")
            raise typer.Exit(1)

        usages = analyze_queries(queries_sql, dialect, schema)
        if usages.query_count == 0:
            console.print("[yellow]No SELECT queries found.[/]")
            raise typer.Exit(1)

        suggestions = generate_suggestions(schema, usages, min_score)

        if output == "table":
            render_table(console, suggestions, min_score)
        elif output == "json":
            console.print(render_json(suggestions))
        else:
            console.print("[red]Unsupported output format.[/]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app(prog_name="sql-index-suggester")
