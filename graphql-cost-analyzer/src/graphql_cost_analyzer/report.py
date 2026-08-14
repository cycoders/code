from rich.table import Table

def render_table(results):
    table = Table(title="Cost Report")
    table.add_column("Field")
    table.add_column("Cost", justify="right")
    for r in results:
        table.add_row(r["field"], str(r["cost"]))
    return table