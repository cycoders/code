import typer

from rich import print as rprint
from rich.progress import track

import sql_erd_cli.parser as parser
import sql_erd_cli.graph_generator as graphgen


app = typer.Typer(help="Generate ERDs from SQL DDL.")


@app.command()
def generate(
    sql_file: typer.FileText = typer.Argument(..., help="SQL DDL file"),
    output: str = typer.Option("erd.png", "--output", "-o", help="Output file (png/svg/pdf)"),
    dialect: str = typer.Option("postgres", "--dialect", "-d", help="SQL dialect (postgres/mysql/sqlite)"),
    layout: str = typer.Option("dot", "--layout", "-l", help="Graphviz layout (dot/neato/fdp)"),
    format_out: str = typer.Option("png", "--format", "-f", help="Output format (png/svg/pdf)"),
    exclude: list[str] = typer.Option([], "--exclude", help="Comma-separated tables to exclude"),
):
    """Generate ERD from SQL DDL."""

    sql_content = sql_file.read()

    rprint(f"[blue]Parsing[/blue] {dialect} DDL...")
    schema = parser.parse_schema(sql_content, dialect)

    for table in exclude:
        schema.tables.pop(table, None)

    if not schema.tables:
        raise typer.Exit(message="No tables found after filtering.")

    rprint("[green]Building graph...[/green]")
    dot = graphgen.generate_erd(schema, layout)

    rprint(f"[yellow]Rendering[/yellow] to {output}...")
    dot.format = format_out
    dot.render(output, cleanup=True, format=format_out)

    rprint(f"[bold green]✓ ERD saved to {output} ({len(schema.tables)} tables)[/bold green]")
