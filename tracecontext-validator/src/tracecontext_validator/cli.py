import click
from rich.console import Console
from tracecontext_validator.core import parse_traceparent

console = Console()

@click.group()
def cli() -> None:
    pass

@cli.command()
@click.option("--header", required=True, help="traceparent header value")
def check(header: str) -> None:
    ctx = parse_traceparent(header)
    if ctx.valid:
        console.print("[green]Valid trace context[/green]")
    else:
        console.print(f"[red]Invalid: {ctx.error}[/red]")