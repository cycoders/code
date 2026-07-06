import typer
from rich.console import Console
from .scanner import scan_path

app = typer.Typer(help="Detect weak PRNG usage")
console = Console()

@app.command()
def main(path: str = ".", format: str = "text") -> None:
    findings = scan_path(path)
    if format == "text":
        for f in findings:
            console.print(f"{f.path}:{f.line} {f.message}")
    else:
        console.print_json([f.__dict__ for f in findings])