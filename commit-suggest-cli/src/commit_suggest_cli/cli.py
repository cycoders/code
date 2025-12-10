import typer
from rich.console import Console
from pathlib import Path

from .parser import parse_diff
from .suggester import suggest_message
from .validator import validate_commit

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Suggest a conventional commit message from git changes")
def suggest(
    stage: typer.Literal["staged", "unstaged", "all"] = "staged",
    repo: Path = typer.Argument(".", help="Path to git repo"),
):
    """Analyze git diff and suggest commit message."""
    try:
        changes = parse_diff(str(repo), stage)
        if not changes["files"]:
            console.print("[yellow]No changes detected.[/] Use git add first.")
            raise typer.Exit(0)
        msg = suggest_message(changes)
        console.print("[bold green]Suggested commit:[/bold green]")
        console.print(msg, markup=False)
    except ValueError as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"[red]Unexpected error:[/red] {str(e)}", err=True)
        raise typer.Exit(1)

@app.command(help="Validate a commit message")
def validate(message: str):
    """Check if message follows conventional commits rules."""
    is_valid, issues = validate_commit(message)
    if is_valid:
        console.print("[green]✓ Valid conventional commit message[/green]")
    else:
        console.print("[red]✗ Invalid:[/red]")
        for issue in issues:
            console.print(f"  [dim]• {issue}[/dim]")
    raise typer.Exit(0 if is_valid else 1)

@app.command(help="List supported commit types")
def types():
    """Show available commit types."""
    types_list = "feat, fix, docs, style, refactor, perf, test, chore, ci, revert"
    console.print(f"Supported types: [bold]{types_list}[/bold]")

if __name__ == "__main__":
    app()
