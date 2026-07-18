import typer
from rich.console import Console
from .core import analyze

app = typer.Typer()
console = Console()

@app.command()
def main(path: str):
    findings = analyze(path)
    for f in findings:
        console.print(f"{f.path}:{f.line} {f.message}")