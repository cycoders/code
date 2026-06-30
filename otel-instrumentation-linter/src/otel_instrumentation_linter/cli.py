import typer
from rich.console import Console
from .scanner import scan_path

app = typer.Typer()
console = Console()

@app.command()
def main(path: str = ".", config: str | None = None):
    findings = scan_path(path, config)
    for f in findings:
        console.print(f)
    raise typer.Exit(1 if findings else 0)