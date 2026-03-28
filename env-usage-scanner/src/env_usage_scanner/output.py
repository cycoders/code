import json
from pathlib import Path
from typing import Dict, Any

from rich.console import Console
from rich.table import Table
from rich import box

import env_usage_scanner.models as models


console = Console()


def print_scan_results(usages: models.UsageMap) -> None:
    """Print rich table of scan results."""
    if not usages:
        console.print("[green]No env vars found.[/green]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Var", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right")
    table.add_column("Files", justify="right")
    table.add_column("Samples", max_width=60)

    for var, usgs in sorted(usages.items()):
        count = len(usgs)
        files = len(set(u.file_path.name for u in usgs))
        samples = " | ".join(u.snippet[:40] for u in usgs[:3])
        table.add_row(var, str(count), str(files), samples)

    console.print(table)


def generate_template(usages: models.UsageMap, output_path: Optional[Path] = None) -> str:
    """Generate .env template string."""
    vars_list = sorted(usages.keys())
    template = "# Auto-generated .env template by env-usage-scanner\n" + "\n".join(f"{v}=" for v in vars_list)

    if output_path:
        output_path.write_text(template)
        console.print(f"[green]Template written to {output_path}[/green]")

    return template


def generate_mermaid_graph(usages: models.UsageMap, output_path: Optional[Path] = None) -> str:
    """Generate Mermaid graph: files --> vars."""
    mermaid = ['```mermaid', 'graph TD']
    for var, usgs in usages.items():
        for usage in set(usgs):  # Dedup per file
            safe_file = usage.file_path.name.replace('"', '\"')
            safe_var = var.replace('"', '\"')
            mermaid.append(f'  "{safe_file}" --> "{safe_var}"')
    mermaid.append('```')

    graph_str = "\n".join(mermaid)

    if output_path:
        output_path.write_text(graph_str)
        console.print(f"[green]Mermaid graph written to {output_path}[/green]")

    return graph_str


def print_unused(defined: set[str], used: set[str]) -> None:
    """Print unused and missing vars."""
    unused = defined - used
    missing = used - defined

    if unused:
        table = Table(title="Unused Vars in .env", box=box.MINIMAL)
        table.add_column("Var")
        for v in sorted(unused):
            table.add_row(v)
        console.print(table)

    if missing:
        table = Table(title="Missing Vars in .env (required by code)", box=box.MINIMAL, title_style="bold red")
        table.add_column("Var")
        for v in sorted(missing):
            table.add_row(v)
        console.print(table)
    else:
        console.print("[green]All used vars are defined in .env![/green]")


def output_json(usages: models.UsageMap, output_path: Optional[Path] = None) -> None:
    """Output JSON for CI/scripts."""
    data: Dict[str, Any] = {}
    for var, usgs in usages.items():
        data[var] = [{
            'file': str(u.file_path),
            'line': u.line_num,
            'snippet': u.snippet,
            'lang': u.lang
        } for u in usgs]

    json_str = json.dumps(data, indent=2)
    if output_path:
        output_path.write_text(json_str)
    else:
        console.print(json_str)
