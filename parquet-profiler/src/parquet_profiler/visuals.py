from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_schema(schema):
    table = Table(title="Schema")
    table.add_column("Field")
    table.add_column("Type")
    table.add_column("Nullable")
    for f in schema.fields:
        table.add_row(f["name"], f["type"], str(f["nullable"]))
    console.print(table)
    console.print(f"Rows: {schema.num_rows:,} | Columns: {schema.num_columns}")

# Integrated in types __rich__
