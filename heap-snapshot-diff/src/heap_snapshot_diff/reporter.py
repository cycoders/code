from rich.table import Table

def render_table(diffs, console):
    table = Table(title="Heap Growth")
    table.add_column("Type")
    table.add_column("Growth", justify="right")
    table.add_column("Delta (bytes)", justify="right")
    for d in diffs:
        table.add_row(d["type"], f"{d['growth']:.1%}", str(d["delta_bytes"]))
    console.print(table)