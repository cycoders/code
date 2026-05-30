import typer
from rich.console import Console
from .engine import lint
from .rules import DEFAULT_RULES

app = typer.Typer(help="PromQL linter")
console = Console()

@app.command()
def check(query: str, config: str = None):
    """Lint a PromQL expression or file."""
    issues = lint(query, DEFAULT_RULES)
    for issue in issues:
        console.print(issue)
    raise typer.Exit(code=1 if issues else 0)