import click
from rich.console import Console
from rich.table import Table

from .parser import parse_url, ParseError
from .auditor import audit

console = Console()

@click.command()
@click.argument("url")
@click.option("--json", is_flag=True, help="Output JSON")
def cli(url: str, json: bool) -> None:
    """Audit a database connection URL."""
    try:
        result = parse_url(url)
        result = audit(result)
        if json:
            click.echo(result.model_dump_json(indent=2))
            return
        table = Table(title="Findings")
        for f in result.findings:
            table.add_row(f.code, f.severity, f.message)
        console.print(table if result.findings else "No issues found")
    except ParseError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(2)