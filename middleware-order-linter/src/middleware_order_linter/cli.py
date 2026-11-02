import typer
from rich.console import Console
from .analyzer import analyze
from .rules import DEFAULT_RULES

app = typer.Typer()
console = Console()

@app.command()
def main(path: str, framework: str = "flask", config: str | None = None):
    """Lint middleware ordering."""
    violations = analyze(path, framework, config)
    for v in violations:
        console.print(v)
    raise typer.Exit(code=1 if violations else 0)