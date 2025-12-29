from rich.console import Console
from rich.table import Table
from rich import box
import json
from datetime import datetime

console = Console()

def display_decoded(header: dict, payload: dict, sig_b64: str):
    """Rich pretty-print decoded JWT."""

    # Header table
    table = Table(title="[bold cyan]Header[/]", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", expand=True)
    for k, v in header.items():
        table.add_row(k, json.dumps(v, separators=(',', ':')))
    console.print(table)

    # Payload table w/ special formatting
    table = Table(title="[bold green]Payload[/]", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Claim", style="green", no_wrap=True)
    table.add_column("Value", expand=True)

    special = ["iss", "sub", "aud", "exp", "nbf", "iat", "jti"]
    for claim in special:
        if claim in payload:
            val = payload[claim]
            if isinstance(val, (int, float)) and claim in ["exp", "iat", "nbf"]:
                try:
                    dt = datetime.utcfromtimestamp(val)
                    val = f"{int(val)} ([dim]{dt.isoformat()}[/dim])"
                except:
                    pass
            table.add_row(claim, str(val))

    for claim in sorted(k for k in payload if k not in special):
        table.add_row(claim, json.dumps(payload[claim], separators=(',', ':')))
    console.print(table)

    console.print(f"\n[dim yellow]Signature (b64url)[/]: [grey50]{sig_b64}[/]\n")