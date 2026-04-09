import typer
from rich.console import Console
from pathlib import Path
import sys

from .core import generate_checklist
from .output import print_console, render_md

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command(help="Generate checklist from git diff")
def diff(
    base: str = typer.Argument("main", help="Base ref (e.g. main, origin/main)"),
    head: str = typer.Argument("HEAD", help="Head ref"),
    fmt: str = typer.Option("console", "--format/-f", help="Output: console, md, json"),
    cwd: Path = typer.Option(Path("."), "--cwd", help="Git repo path"),
):
    """Generate a tailored code review checklist."""
    try:
        items = generate_checklist(base, head, str(cwd))
        if not items:
            console.print("[green]No changes detected. Perfect! 🎉[/green]")
            raise typer.Exit(0)
        if fmt == "console":
            print_console(items)
        elif fmt == "md":
            print(render_md(items), end="")
        elif fmt == "json":
            import json
            print(json.dumps([{
                "title": i.title,
                "description": i.description,
                "priority": i.priority,
                "suggested_command": i.suggested_command
            } for i in items], indent=2))
        else:
            console.print("[red]Invalid format. Use: console, md, json[/red]")
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red bold]Error:[/red bold] {e}")
        console.print("[dim]Tip: Run in a git repo. Use 'git status' first.[/dim]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Git error:[/red] {e}. Ensure refs exist: git fetch.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def current():
    """Shortcut: diff vs main."""
    diff("main", "HEAD")

if __name__ == "__main__":
    app()