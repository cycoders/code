import logging
from pathlib import Path
import sys

from rich import print as rprint
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from typer import Typer, Argument, Option, Exit

import class_diagram_cli  # noqa

from .collector import CodebaseCollector
from .generator import MermaidGenerator


app = Typer(add_completion=False)
console = Console(file=sys.stderr)


@app.command(help="Generate class diagram from Python codebase")
def diagram(
    root: Path = Argument(".", help="Root directory to scan"),
    output: Path = Option(
        "diagram.mmd", "--output", "-o", help="Output Mermaid file"
    ),
    exclude: list[str] = Option(
        None, "--exclude", help="Glob patterns to exclude (e.g. '**/test*.py')"
    ),
) -> None:
    """Scan Python files and generate Mermaid class diagram."""

    if not root.exists():
        rprint(f"[red]❌ Path not found: {root}")
        raise Exit(code=1)

    # Collect
    collector = CodebaseCollector(root, exclude or [])

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Scanning Python files...", total=None)
        classes = collector.collect()
        progress.remove_task(task)

    if not classes:
        rprint("[red]❌ No classes found! Check --exclude or add Python files.")
        raise Exit(code=1)

    rprint(f"[green]✅ Found {len(classes)} classes across modules.")

    # Generate
    generator = MermaidGenerator(classes, console)
    diagram_text = generator.generate()

    # Save
    output.write_text(diagram_text, encoding="utf-8")
    rprint(f"[green]💾 Diagram saved: [bold]{output}[/bold]")
    rprint("[blue]👉 Paste into https://mermaid.live or GitHub.md!")

    # Summary table
    table = Table(title="Classes Overview", show_header=True, header_style="bold magenta")
    table.add_column("Module", style="cyan")
    table.add_column("Class", style="green")
    table.add_column("Bases", max_width=20)
    table.add_column("Methods", justify="right")
    table.add_column("Attrs", justify="right")

    for cls in sorted(classes, key=lambda c: c.module + c.name)[:20]:
        bases_str = ", ".join(cls.bases[:3]) + (
            "..." if len(cls.bases) > 3 else ""
        )
        table.add_row(
            cls.module,
            cls.name,
            bases_str,
            str(len(cls.methods)),
            str(len(cls.attributes)),
        )

    if len(classes) > 20:
        table.add_row("...", f"and {len(classes)-20} more", "", "", "")

    console.print(table)


if __name__ == "__main__":
    app()
