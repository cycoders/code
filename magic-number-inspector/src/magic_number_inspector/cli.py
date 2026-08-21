import typer
from rich.console import Console
from rich.table import Table
from .inspector import identify

app = typer.Typer(help="Identify file types via magic bytes")
console = Console()

@app.command()
def main(paths: list[str], format: str = "table", recursive: bool = False):
    results = []
    for p in paths:
        res = identify(p, recursive=recursive)
        results.extend(res)
    if format == "json":
        import json
        console.print_json(json.dumps(results))
    else:
        table = Table("path", "type", "confidence")
        for r in results:
            table.add_row(r["path"], r["type"], str(r["confidence"]))
        console.print(table)