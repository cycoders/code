import typer
from pathlib import Path
import sys

from rich.console import Console
from rich.markdown import Markdown

from .detector import detect_project
from .generator import render_readme


console = Console()
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


@app.command(help="Scan project and show detected info")
def scan(path: Path = typer.Argument(Path("."), help="Project path")):
    """Scan project for stacks, metadata, conventions."""

    if not path.is_dir():
        typer.echo("❌ Invalid path", err=True)
        raise typer.Exit(1)

    data = detect_project(path)
    console.print("[bold green]Detected:[/bold green]")
    console.print(f"  Stacks: {', '.join(data['stacks']) or 'none'}")
    console.print(f"  Project: {data['project_name']}")
    console.print(f"  Description: {data['description']}")
    console.print(f"  Tests: {'✅' if data['has_tests'] else '❌'}")
    console.print(f"  CI/CD: {'✅' if data['has_ci'] else '❌'}")
    console.print(f"  Features: {', '.join(data['features']) or 'none'}")


@app.command(help="Generate README.md")
def generate(
    path: Path = typer.Argument(Path("."), help="Project path"),
    output: Path = typer.Option("README.md", "--output", "-o", help="Output file"),
    dry_run: bool = typer.Option(False, "--dry-run", "-D", help="Preview only"),
):
    """Generate polished README.md from project scan."""

    if not path.is_dir():
        typer.echo("❌ Invalid path", err=True)
        raise typer.Exit(1)

    console.print("🔍 Scanning project...")
    data = detect_project(path)
    md_content = render_readme(data)

    if dry_run:
        console.print("\n" + "="*80)
        console.print(Markdown(md_content))
        console.print("="*80)
        return

    output.write_text(md_content, encoding="utf-8")
    console.print(f"✅ Wrote [bold]{output}[/bold]")


def main():
    if len(sys.argv) == 1:
        app(prog_name="smart-readme-generator")
    else:
        app()


if __name__ == "__main__":
    main()
