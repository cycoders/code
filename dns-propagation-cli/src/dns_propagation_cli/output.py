import json
import csv
from io import StringIO
from typing import List

import rich
from rich.table import Table
from rich.console import Console

from .models import PropagationResult


console = Console()


def print_propagation_table(results: List[PropagationResult]):
    table = Table(title="[bold cyan]DNS Propagation Status[/]")
    table.add_column("Resolver", style="cyan", no_wrap=True)
    table.add_column("Location", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Response", style="green")
    table.add_column("Latency (ms)", justify="right")

    total = len(results)
    propagated = sum(1 for r in results if r.status == "✅ Propagated")
    pending = sum(1 for r in results if r.status == "❌ Pending")
    errors = total - propagated - pending
    caption = (
        f"[bold green]✅ Propagated[/]: {propagated}/{total} "
        f"({propagated/total*100:.1f}%)  "
        f"[bold yellow]❌ Pending[/]: {pending}  "
        f"[bold red]⚠️ Errors[/]: {errors}"
    )
    table.caption = caption

    for r in results:
        resp = r.response or r.error or "-"
        table.add_row(
            r.resolver_name,
            r.location,
            r.status,
            resp,
            f"{r.latency:.0f}",
        )

    console.print(table)


def print_json(results: List[PropagationResult]):
    data = [{
        "resolver_name": r.resolver_name,
        "ip": r.ip,
        "location": r.location,
        "status": r.status,
        "response": r.response,
        "latency": r.latency,
        "error": r.error,
    } for r in results]
    print(json.dumps(data, indent=2))


def print_csv(results: List[PropagationResult]):
    if not results:
        return
    output = StringIO()
    fieldnames = [
        "resolver_name",
        "ip",
        "location",
        "status",
        "response",
        "latency",
        "error",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow({
            "resolver_name": r.resolver_name,
            "ip": r.ip,
            "location": r.location,
            "status": r.status,
            "response": r.response,
            "latency": r.latency,
            "error": r.error,
        })
    print(output.getvalue(), end="")