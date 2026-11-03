import typer
from rich.console import Console
from .core import audit_project

app = typer.Typer()
console = Console()

@app.command()
def main(path: str = ".", format: str = "text", fail_on: str = "warning"):
    """Audit packaging configuration of a Python project."""
    results = audit_project(path)
    if format == "json":
        import json
        console.print(json.dumps(results, indent=2))
    else:
        for r in results:
            console.print(f"[{r['severity']}] {r['message']}")
    if any(r['severity'] in ("error", fail_on) for r in results):
        raise typer.Exit(1)