from rich.table import Table
from typing import Any

def render_terminal(result: Any, console) -> None:
    table = Table(title="Flamegraph Diff")
    table.add_column("Frame")
    table.add_column("Delta", justify="right")
    table.add_column("p-value")
    for r in result.regressions:
        table.add_row(r['frame'], f"+{r['delta']}", f"{r['p']:.4f}", style="red")
    console.print(table)

def render_html(result: Any) -> str:
    return "<html><body><h1>Diff ready</h1></body></html>"