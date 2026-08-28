from rich.table import Table
from rich.console import Console
from crypto_agility_scanner.models import Finding
from pathlib import Path

def render(findings, fmt, output, console: Console):
    if fmt == "text":
        table = Table(title="Crypto Findings")
        table.add_column("File")
        table.add_column("Line")
        table.add_column("Algorithm")
        table.add_column("Suggestion")
        for f in findings:
            table.add_row(str(f.file), str(f.line), f.algorithm, f.suggestion)
        console.print(table)
    elif fmt == "json":
        import json
        data = [f.__dict__ for f in findings]
        (Path(output) if output else Path("-")).write_text(json.dumps(data, default=str))