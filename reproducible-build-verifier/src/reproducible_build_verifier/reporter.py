from rich.table import Table
from typing import List, Dict

def report(findings: List[Dict], fmt: str, console):
    if fmt == 'json':
        console.print(findings)
        return
    table = Table(title="Non-determinism Findings")
    table.add_column("Type")
    table.add_column("Location")
    table.add_column("Detail")
    for f in findings:
        table.add_row(f['type'], f.get('file',''), f['detail'])
    console.print(table)