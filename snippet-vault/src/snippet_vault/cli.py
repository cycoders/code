import sys
import os
import shutil
import subprocess
import tempfile
import json
import typer
from datetime import datetime
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.box import ROUNDED
from rich.prompt import Confirm, Prompt

from . import __version__
from .config import load_config, get_db_path
from .db import SnippetDB
from .models import Snippet


app = typer.Typer(add_completion=False)
console = Console()
db: Optional[SnippetDB] = None


def _get_db(state: bool = True) -> SnippetDB:
    global db
    if db is None:
        config = load_config()
        db_path = get_db_path(config)
        db = SnippetDB(db_path)
    return db


@app.command()
def version():
    """Show version."""
    console.print(f"snippet-vault {__version__}")


@app.command()
def init():
    """Initialize database (auto-creates)."""
    db_path = get_db_path(load_config())
    _get_db()
    console.print(f"[green]✓ Database ready:[/green] {db_path}")


@app.command()
def add(
    title: str = typer.Argument(..., help="Snippet title"),
    language: str = typer.Option("text", "--language/-l"),
    tags: str = typer.Option("", "--tags/-t", help="Comma-separated tags"),
):
    """Add new snippet (content via stdin)."""
    content = sys.stdin.read().strip()
    if not content:
        raise typer.BadParameter(
            "No content. Pipe it: 'cat file.py | snip add ...'"
        )
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    snippet = Snippet(title=title, language=language, tags=tag_list, content=content)
    db = _get_db()
    sid = db.add(snippet)
    console.print(f"[green]✓ Added:[/green] #{sid} {title}")


@app.command()
def list_(
    search: str = typer.Option("", "--search/-s"),
    tag_filter: str = typer.Option("", "--tag/-T"),
    limit: int = typer.Option(20, "--limit/-L"),
):
    """List snippets (filtered/sorted recent)."""
    db = _get_db()
    snippets = db.search(search, limit)
    if tag_filter:
        ltag = tag_filter.lower()
        snippets = [
            s for s in snippets if ltag in [t.lower() for t in s.tags]
        ]
    if not snippets:
        console.print("[yellow]No snippets found.[/yellow]")
        raise typer.Exit()

    table = Table(box=ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Lang")
    table.add_column("Tags")
    table.add_column("Created")
    table.add_column("Preview")

    for s in snippets:
        preview = (
            (s.content[:60] + "...").replace("\n", " ") if len(s.content) > 60 else s.content
        )
        table.add_row(
            str(s.id),
            s.title[:30] + "..." if len(s.title) > 30 else s.title,
            s.language,
            ",".join(s.tags[:2]),
            s.created_at.strftime("%m/%d") if s.created_at else "",
            preview,
        )
    console.print(table)


@app.command()
def show(snippet_id: int):
    """Show full highlighted snippet."""
    db = _get_db()
    snippet = db.get(snippet_id)
    if not snippet:
        raise typer.BadParameter(f"Snippet #{snippet_id} not found")
    console.print(f"[bold cyan]#{snippet.id}: {snippet.title}[/bold cyan]")
    console.print(
        f"[dim]Lang: {snippet.language} | Tags: {', '.join(snippet.tags)} | {snippet.created_at:%Y-%m-%d %H:%M}[/dim]"
    )
    syntax = Syntax(
        snippet.content,
        snippet.language,
        theme="github-dark",
        line_numbers=True,
        word_wrap=True,
    )
    console.print(syntax)


@app.command()
def rename(
    snippet_id: int,
    title: Optional[str] = typer.Option(None, "--title"),
    tags: Optional[str] = typer.Option(None, "--tags"),
):
    """Rename/update title/tags."""
    db = _get_db()
    snippet = db.get(snippet_id)
    if not snippet:
        raise typer.BadParameter(f"Snippet #{snippet_id} not found")
    if title:
        snippet.title = title
    if tags:
        snippet.tags = [t.strip() for t in tags.split(",") if t.strip()]
    db.update(snippet)
    console.print("[green]✓ Updated meta.[/green]")


@app.command()
def edit_content(snippet_id: int):
    """Edit snippet content in $EDITOR."""
    db = _get_db()
    snippet = db.get(snippet_id)
    if not snippet:
        raise typer.BadParameter(f"Snippet #{snippet_id} not found")
    editor = os.environ.get("EDITOR", "nano")
    if not shutil.which(editor):
        raise typer.BadParameter(
            f"Editor '{editor}' not found. Install or set $EDITOR (e.g., vim/nano/code -w)."
        )
    fd, tmp_path = tempfile.mkstemp(suffix=f".{snippet.language}", prefix="snip-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(snippet.content)
        subprocess.run([editor, tmp_path], check=True)
        with open(tmp_path, "r", encoding="utf-8") as f:
            new_content = f.read()
        if new_content.strip() == snippet.content.strip():
            console.print("[yellow]No changes.[/yellow]")
            return
        snippet.content = new_content
        db.update(snippet)
        console.print("[green]✓ Content updated.[/green]")
    finally:
        os.unlink(tmp_path)


@app.command()
def delete(snippet_id: int):
    """Delete snippet (confirm)."""
    db = _get_db()
    snippet = db.get(snippet_id)
    if not snippet:
        raise typer.BadParameter(f"Snippet #{snippet_id} not found")
    console.print(f"[bold red]Delete '{snippet.title}'?[/bold red]")
    if Confirm.ask():
        if db.delete(snippet_id):
            console.print("[green]✓ Deleted.[/green]")
        else:
            console.print("[red]Failed.[/red]")


@app.command()
def export(snippet_id: int, fmt: str = typer.Option("md", "--format")):
    """Export to stdout (md/json)."""
    db = _get_db()
    snippet = db.get(snippet_id)
    if not snippet:
        raise typer.BadParameter(f"Snippet #{snippet_id} not found")
    if fmt == "md":
        print(f"# {snippet.title}")
        print(f"\n**Tags:** {', '.join(snippet.tags)} | **Lang:** {snippet.language}")
        print("\n```" + snippet.language)
        print(snippet.content)
        print("```")
    elif fmt == "json":
        print(json.dumps(snippet.to_dict(), indent=2))
    else:
        raise typer.BadParameter("Format: md or json")


if __name__ == "__main__":
    app()
