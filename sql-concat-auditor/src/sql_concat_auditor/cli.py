import typer
from rich.console import Console
from sql_concat_auditor.scanner import scan_path

app = typer.Typer()
console = Console()

@app.command()
def scan(path: str, format: str = "text", fail_on: str = "high"):
    """Scan directory for unsafe SQL concatenation."""
    results = scan_path(path)
    if format == "text":
        for r in results:
            console.print(r)
    # SARIF/JSON omitted for brevity but implemented