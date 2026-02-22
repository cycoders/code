from typing import Dict
from rich.console import Console
from rich.table import Table


def print_env_diff(env1: Dict[str, str], env2: Dict[str, str], console: Console) -> None:
    """Print pretty diff table."""
    table = Table(title="[bold magenta]Environment Diff[/]", box="heavy")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Env1 (left)", style="green")
    table.add_column("Env2 (right)", style="blue")
    table.add_column("Status", style="yellow")

    all_keys = sorted(set(env1) | set(env2))
    for key in all_keys:
        v1 = env1.get(key, "[dim]---[/]")
        v2 = env2.get(key, "[dim]---[/]")
        if key not in env1:
            status = "[bold red]added[/]"
        elif key not in env2:
            status = "[bold green]removed[/]"
        elif v1 == v2:
            status = "[bold dim]same[/]"
            v1 = v2 = f"[dim]{v1}[/]"
        else:
            status = "[bold yellow]changed[/]"
        table.add_row(key, v1, v2, status)

    console.print(table)