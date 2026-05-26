import typer
from rich.console import Console
from .scanner import scan_directory

app = typer.Typer()
console = Console()

@app.command()
def main(path: str = ".", config: str | None = None, fail_on_high: bool = False):
    """Run resource leak audit."""
    issues = scan_directory(path, config)
    for issue in issues:
        console.print(issue)
    if fail_on_high and any(i.severity == "high" for i in issues):
        raise typer.Exit(code=1)