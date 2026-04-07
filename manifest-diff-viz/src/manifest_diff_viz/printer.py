from typing import Dict, List, Any
import json
from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich.tree import Tree
from rich.text import Text

def print_diff_summary(
    diffs: Dict[str, List[Dict[str, Any]]],
    console: Console,
    verbose: bool = False,
) -> None:
    """Print rich summary and details."""
    if not diffs:
        return

    # Summary table
    table = Table(title="[bold]Manifest Diff Summary[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Resource", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Change Count", justify="right")

    for res_key, changes in diffs.items():
        status = _get_status_emoji(changes[0]['type'])
        table.add_row(res_key[:50] + '...' if len(res_key) > 50 else res_key, status, str(len(changes)))

    console.print(table)

    # Detailed trees
    for res_key, changes in diffs.items():
        tree = Tree(f"[bold cyan]{res_key}[/bold cyan]", guide_style="dim")
        _add_changes_to_tree(changes, tree)
        console.print(tree)
        console.print()  # Spacer

def _get_status_emoji(change_type: str) -> str:
    return {'added': '➕', 'removed': '➖', 'modified': '⚡'}.get(change_type, '?')

def _add_changes_to_tree(changes: List[Dict[str, Any]], tree: Tree) -> None:
    """Recurse changes into rich tree."""
    for change in changes:
        ctype = change['type']
        path_str = '.'.join(change['path'])
        style = {
            'added': 'bold green',
            'removed': 'bold red',
            'modified': 'bold yellow'
        }.get(ctype, 'bold white')

        node_label = Text(f"{ctype.upper()} {path_str}", style=style)
        node = tree.add(node_label)

        if 'old' in change and 'new' in change:
            old_fmt = _format_value(change['old'])
            new_fmt = _format_value(change['new'])
            node.add(f"[dim]old:[/dim] {old_fmt} → [dim]new:[/dim] {new_fmt}")
        elif 'value' in change:
            val_fmt = _format_value(change['value'])
            node.add(f"[dim]value:[/dim] {val_fmt}")

def _format_value(v: Any, max_len: int = 80) -> str:
    """Pretty format value for display."""
    if v is None:
        return "null"
    if isinstance(v, (str, int, float, bool)):
        return repr(v)
    try:
        # Try compact JSON
        s = json.dumps(v, sort_keys=True, separators=(',', ':'))
        if len(s) < max_len:
            return s
    except (TypeError, ValueError):
        pass
    return f"{str(v)[:max_len]}..."