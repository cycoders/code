import typer
from rich.console import Console
from .scanner import scan_repository

app = typer.Typer(help="Audit correlation ID propagation")
console = Console()

@app.command()
def scan(path: str = ".", format: str = "text", fail_on: str = "missing"):
    """Scan repository for correlation ID issues."""
    issues = scan_repository(path)
    if format == "sarif":
        console.print("SARIF output not shown in this demo")
    else:
        for issue in issues:
            console.print(issue)
    if fail_on == "missing" and issues:
        raise typer.Exit(code=1)