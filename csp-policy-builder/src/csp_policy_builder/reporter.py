from pathlib import Path
import logging
from collections import Counter
from typing import List, Optional

import rich.console
import rich.table
import rich.progress
from rich import box

from .types import Resource


console = rich.console.Console()
progress = rich.progress.Progress()


def report_resources(resources: List[Resource], policy: str, score: int) -> None:
    """Rich report."""
    console.rule("[bold blue]CSP Policy Builder Report[/]")

    console.print(f"[bold green]Generated Policy:[/bold green]\n[white]{policy}[/]")
    console.print(f"[bold yellow]Strictness Score: {score}/100[/]")

    # Summary table
    dir_count = Counter(r.directive for r in resources)
    table = rich.table.Table(title="Resource Summary", box=box.ROUNDED)
    table.add_column("Directive", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Inline", justify="right", style="magenta")
    table.add_column("External", justify="right", style="blue")

    for directive, count in dir_count.most_common():
        inline = sum(1 for r in resources if r.directive == directive and r.is_inline)
        external = count - inline
        table.add_row(directive, str(count), str(inline), str(external))

    console.print(table)

    # Top hosts
    hosts = Counter(r.host for r in resources if r.host)
    if hosts:
        console.print("\n[bold]Top Domains:[/] " + " | ".join(f"[blue]{h}: {c}[/blue]" for h, c in hosts.most_common(5)))


def audit(resources: List[Resource], policy_str: str) -> List[str]:
    """Simple audit: potential violations."""
    violations = []
    # Basic: check if resource host/hash in policy (simplified)
    for res in resources[:20]:  # limit
        if "unsafe" not in policy_str and res.is_inline and not res.hash_value:
            violations.append(f"Inline {res.directive} without hash/nonce: {res.url[:50]}...")
        if res.host and res.host not in policy_str:
            violations.append(f"Unallowed host {res.host} for {res.directive}")
    if violations:
        console.print("[bold red]Potential Violations:[/]")
        for v in violations:
            console.print(f"  [red]{v}[/]")
    else:
        console.print("[bold green]✓ No violations detected[/]")
    return violations
