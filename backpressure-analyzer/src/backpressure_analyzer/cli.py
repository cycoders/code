import typer
from rich.console import Console
from .analyzer import analyze_path

app = typer.Typer()
console = Console()

@app.command()
def main(path: str, metrics: str | None = None, format: str = "rich"):
    """Analyze async code for backpressure risks."""
    findings = analyze_path(path, metrics)
    if format == "rich":
        for f in findings:
            console.print(f)
    else:
        print(findings)