from typing import List
import textwrap
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from .core import ChecklistItem

console = Console()

def print_console(items: List[ChecklistItem]) -> None:
    table = Table(title="[bold cyan]Code Review Checklist[/bold cyan]", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Priority", justify="center", style="bold", no_wrap=True, width=12)
    table.add_column("Title", style="bold", no_wrap=False)
    table.add_column("Description")
    table.add_column("Suggested Command", no_wrap=True)

    for item in items:
        pri_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[item.priority]
        pri_color = {"high": "red", "medium": "yellow", "low": "green"}[item.priority]
        pri_text = Text.assemble(
            (pri_emoji, "bold " + pri_color),
            (f" {item.priority.upper()}", pri_color),
        )
        cmd = item.suggested_command or "—"
        table.add_row(str(pri_text), item.title, textwrap.fill(item.description, 50), f"`{cmd}`" if cmd != "—" else "")

    console.print(table)
    console.print("\n[bold green]✅ Run high-priority first![/bold green]")

def render_md(items: List[ChecklistItem]) -> str:
    lines = [
        "# Code Review Checklist\n\n",
        "*Generated from git diff. Prioritize high items.*\n\n",
    ]
    by_pri: Dict[str, List[ChecklistItem]] = {"high": [], "medium": [], "low": []}
    for item in items:
        by_pri[item.priority].append(item)

    for pri in ["high", "medium", "low"]:
        lines.append(f"## {pri.upper()} ({len(by_pri[pri])} items)\n\n")
        for item in by_pri[pri]:
            lines.extend([
                f"### {item.title}\n\n",
                f"{item.description}\n\n",
            ])
            if item.suggested_command:
                lines.append(f"**Run:** `cd {os.getcwd()}; {item.suggested_command}`\n\n")
        lines.append("\n---\n\n")

    return "".join(lines)