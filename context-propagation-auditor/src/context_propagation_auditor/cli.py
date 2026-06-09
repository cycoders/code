import typer
from rich.console import Console
from .scanner import scan_directory

app = typer.Typer(help="Audit context propagation")
console = Console()

@app.command()
def main(path: str = "."):
    findings = scan_directory(path)
    for f in findings:
        console.print(f"{f.path}:{f.line} {f.message}", style="red")
    raise typer.Exit(code=1 if findings else 0)