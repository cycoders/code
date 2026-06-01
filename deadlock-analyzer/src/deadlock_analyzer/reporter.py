from rich.console import Console
from rich.table import Table
from .models import AnalysisResult

console = Console()

def report(result: AnalysisResult):
    if not result.cycles:
        console.print("[green]No deadlock cycles detected.[/green]")
        return
    table = Table(title="Potential Deadlock Cycles")
    table.add_column("Cycle")
    for cycle in result.cycles:
        names = " -> ".join(n.name for n in cycle)
        table.add_row(names)
    console.print(table)