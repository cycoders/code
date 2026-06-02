from rich.table import Table
from rich.console import Console

def render(data):
    console = Console()
    table = Table(title="Contention Report")
    table.add_column("Site")
    table.add_column("Acquires")
    table.add_column("Total Wait (s)")
    for site, (count, wait) in sorted(data.items(), key=lambda x: -x[1][1]):
        table.add_row(site, str(count), f"{wait:.4f}")
    console.print(table)