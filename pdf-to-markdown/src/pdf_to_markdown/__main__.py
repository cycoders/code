#!/usr/bin/env python3
"""CLI entrypoint."""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.traceback import install

from pdf_to_markdown import __version__
from pdf_to_markdown.converter import iter_pages_md, get_page_indices

install(show_locals=True)

app = typer.Typer(add_completion=False)
console = Console()


def version_callback(ctx: typer.Context, param: Any, value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def convert(  # noqa: PLR0913
    input_pdf: Path = typer.Argument(..., exists=True, help="Input PDF path"),
    output: Path = typer.Option(Path("output.md"), "-o", "--output", help="Output MD"),
    pages: str = typer.Option(None, "--pages", help="e.g. '1-3,5'"),
    preview: bool = typer.Option(False, "--preview"),
    no_tables: bool = typer.Option(False, "--no-tables"),
    version: bool = typer.Option(False, "--version", callback=version_callback),
) -> None:
    """Convert PDF to Markdown."""
    input_path = str(input_pdf)
    try:
        indices = get_page_indices(input_path, pages)
        num_pages = len(indices)
        console.print(f"📄 Processing {num_pages} pages...")

        md_parts: list[str] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            console=console,
        ) as progress:
            task = progress.add_task("Converting...", total=num_pages)
            for page_md in iter_pages_md(input_path, pages, no_tables):
                md_parts.append(page_md)
                progress.update(task, advance=1)

        md = "\n\n--- Page Break ---\n\n".join(md_parts)

        if preview:
            console.print(md)
        else:
            output.write_text(md, "utf-8")
            console.print(f"✅ Wrote [bold cyan]{output}[/] ({len(md)=:.0f} chars)")

    except FileNotFoundError:
        typer.echo("❌ PDF file not found.", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()