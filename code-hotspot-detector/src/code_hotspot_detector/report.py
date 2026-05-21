from rich.table import Table

def render_table(results, console):
    table = Table(title="Code Hotspots")
    table.add_column("Path")
    table.add_column("Churn", justify="right")
    table.add_column("Complexity", justify="right")
    table.add_column("Risk", justify="right")
    for r in results:
        table.add_row(r['path'], str(r['churn']), str(r['complexity']), str(r['risk']))
    console.print(table)