from rich.table import Table

def render(result, fmt, console):
    if fmt == 'text':
        table = Table(title="Drift Report")
        for r in result:
            table.add_row(r['target'], str(len(r['diff'])))
        console.print(table)