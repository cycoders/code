import typer
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .extractor import extract_critical_css


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def extract(
    html_input: str = typer.Argument(..., help="HTML file path or URL"),
    css_files: List[Path] = typer.Option([], "--css", help="Additional CSS files"),
    viewport_height: int = typer.Option(800, "--viewport-height", min=400, max=2000, help="Simulated viewport height (px)"),
    output: Path = typer.Option("critical.css", "--output/-o", help="Output CSS file"),
    inline_styles: bool = typer.Option(False, "--inline-styles", help="Include <style> tags"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print to stdout, no file write"),
) -> None:
    """Extract critical CSS for above-the-fold content."""
    try:
        css_content = extract_critical_css(
            html_input,
            css_files,
            viewport_height,
            inline_styles,
        )
        if dry_run:
            console.print(css_content)
            return
        output.write_text(css_content, encoding="utf-8")
        console.print(f"[green]✓[/green] Critical CSS saved to [blue]{output}[/blue] ({len(css_content)} bytes)")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()