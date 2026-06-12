from rich.table import Table

def render_table(p50, p95):
    table = Table(title="Capacity Forecast")
    table.add_column("Day")
    table.add_column("p50")
    table.add_column("p95")
    for i in range(min(10, len(p50))):
        table.add_row(str(i+1), f"{p50[i]:.1f}", f"{p95[i]:.1f}")
    return table