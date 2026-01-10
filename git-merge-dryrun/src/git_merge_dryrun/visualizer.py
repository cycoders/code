from typing import List
from pathlib import Path
import subprocess
from rich.console import Console, ConsoleOptions
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

DIFF_SYNTAX = "diff"

def show_merge_preview(
    console: Console,
    source: str,
    target: str,
    conflicts: List[str],
    incoming: List[str],
    graph: str,
    base: str,
    repo_path: Path,
    show_diffs: bool,
):
    """Render the full merge preview using Rich."""

    # Header
    title = Text(f"Previewing merge of '{target}' into '{source}'", style="bold magenta")
    console.print(Panel(title, title="[bold cyan]Git Merge Dryrun[/bold cyan]", expand=False))
    console.print()

    # Conflicts
    if conflicts:
        console.print("[bold red]❌ Conflicts detected:[/bold red]")
        table = Table("File", show_header=True, header_style="bold red")
        for file_path in conflicts:
            table.add_row(file_path)
        console.print(table)
        console.print()

        if show_diffs:
            console.print("[bold yellow]📄 Detailed Diffs:[/bold yellow]")
            for file_path in conflicts:
                try:
                    diff1, diff2 = get_conflict_diffs(repo_path, file_path, base, source, target)
                    console.print(f"\n[bold]{file_path}[/bold]")
                    if diff1.strip():
                        console.print(Syntax(diff1, DIFF_SYNTAX, line_numbers=True))
                    console.print("[dim]─" * 50)
                    if diff2.strip():
                        console.print(Syntax(diff2, DIFF_SYNTAX, line_numbers=True))
                    console.print()
                except Exception as e:
                    console.print(f"[red]Failed to load diff for {file_path}: {e}[/red]")
        else:
            console.print("[dim]Use --show-diffs for detailed previews[/dim]")
    else:
        console.print("[bold green]✅ No conflicts![/bold green]")

    console.print()

    # Incoming commits
    if incoming:
        console.print("[bold blue]📋 Incoming Commits[/bold blue]")
        table = Table("Hash", "Message", show_header=True, header_style="bold blue")
        for line in incoming[:10]:  # top 10
            if line:
                hash_, msg = line.split(" ", 1)
                table.add_row(hash_[:8], msg)
        console.print(table)
        if len(incoming) > 10:
            console.print(f"[dim]... and {len(incoming) - 10} more[/dim]")
    else:
        console.print("[green]No new commits[/green]")

    console.print()

    # Graph
    console.print(Panel(graph or "[dim]No graph (shallow repo?)[/dim]", title="[bold green]Current Commit Graph[/bold green]"))

    # Post-merge note
    parents = f"'{source}' ({source[:8]}) and '{target}' ({target[:8]})" if source != "HEAD" else f"HEAD and '{target}' ({target[:8]})"
    console.print(
        Panel(
            f"[bold blue]🔮 Post-merge[/bold blue]: New merge commit with parents {parents}\n"
            f"[dim]Run `git merge {target}` to apply (or `--ff-only` / `--no-ff`)"[/dim]",
            title="Next Steps",
        )
    )

    console.print()