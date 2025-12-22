import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .optimizer import parse_schema, diagnose

app = typer.Typer(help="Diagnose SQL performance issues.")
console = Console()

@app.command(help="Analyze a query against schema.")
def analyze(
    schema_path: Path = typer.Argument(..., help="Path to schema.sql (CREATE TABLE/INDEX)"),
    query_path: Path = typer.Argument(..., help="Path to query.sql"),
    dialect: str = typer.Option("postgres", help="SQL dialect (postgres, mysql, duckdb, etc.)"),
):
    """Diagnose query performance."""
    try:
        schema_content = schema_path.read_text()
        tables = parse_schema(schema_content, dialect)
        if not tables:
            typer.echo("⚠️  No tables parsed from schema.", err=True)
            raise typer.Exit(1)

        query = query_path.read_text()
        console.print(Panel(query, title="[bold cyan]Original Query[/]", expand=False))

        console.print(f"[dim]Schema tables: {', '.join(tables.keys())}[/]")

        issues = diagnose(tables, query, dialect)

        if not issues:
            console.print("[bold green]✅ No issues detected! Your query looks optimized.[/]")
            raise typer.Exit(0)

        table = Table(title="[bold yellow]Query Doctor Diagnosis[/]")
        table.add_column("Severity", style="cyan")
        table.add_column("Issue")
        table.add_column("Suggestion", style="green")

        severity_style = {"high": "red", "medium": "yellow", "low": "blue"}
        for issue in issues:
            sev = f"[{severity_style.get(issue['severity'], 'white')}]{issue['severity'].upper()}[/{severity_style.get(issue['severity'], 'white')} ]"
            table.add_row(sev, issue['description'], issue['suggestion'])

        console.print(table)
        summary = f"[bold]Found {len(issues)} issue{'s' if len(issues) != 1 else ''} ({sum(1 for i in issues if i['severity']=='high')} HIGH)[/bold]"
        console.print(summary)

    except FileNotFoundError as e:
        typer.echo(f"❌ File not found: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Analysis failed: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()