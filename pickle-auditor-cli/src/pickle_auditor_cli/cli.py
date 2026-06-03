import typer
from rich.console import Console
from .scanner import scan_directory

app = typer.Typer()
console = Console()

@app.command()
def main(path: str = ".", config: str | None = None):
    findings = scan_directory(path, config)
    for f in findings:
        console.print(f"[red]{f.severity}[/red] {f.file}:{f.line} {f.message}")