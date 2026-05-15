import click
from rich.console import Console
from rich.table import Table

from .parser import parse_exposition
from .analyzer import estimate_cardinality

console = Console()


@click.group()
def main() -> None:
    pass


@main.command()
@click.option("--threshold", default=1000, show_default=True)
@click.option("--format", "fmt", default="table", type=click.Choice(["table", "json"]))
@click.argument("file", type=click.File("r"), default="-")
def analyze(file, threshold: int, fmt: str) -> None:
    metrics = list(parse_exposition(file))
    results = estimate_cardinality(metrics, threshold)
    if fmt == "json":
        click.echo(results)
        return
    table = Table(title="High Cardinality Metrics")
    table.add_column("Metric")
    table.add_column("Cardinality", justify="right")
    table.add_column("Severity")
    for r in results:
        table.add_row(r["metric"], str(r["cardinality"]), r["severity"])
    console.print(table)


if __name__ == "__main__":
    main()