import json
from typing import Dict, Any
from pathlib import Path
import rich.table
import rich.panel
import rich.console
import rich.syntax
from jinja2 import Template

from csv_profiler import __version__

console = rich.console.Console()

templates_dir = Path(__file__).parent / "templates"


def render_table(data: Dict[str, Any]) -> None:
    """Rich console output."""
    overview = data["overview"]
    columns = data["columns"]
    anoms = data["anomalies"]

    # Overview table
    ov_table = rich.table.Table(title="📊 Overview")
    ov_table.add_column("Metric", style="cyan")
    ov_table.add_column("Value", style="magenta")
    ov_table.add_row("Rows", str(overview["rows"]))
    ov_table.add_row("Columns", str(overview["cols"]))
    ov_table.add_row("Duplicates %", f"{overview['dupe_pct']:.2f}")
    console.print(ov_table)

    # Columns summary
    col_table = rich.table.Table(title="📈 Column Summary", expand=True)
    col_table.add_column("Column", style="cyan")
    col_table.add_column("Null %")
    col_table.add_column("Unique %")
    col_table.add_column("Type")
    col_table.add_column("Top")

    for col, info in columns.items():
        top = str(info["top_values"][0]) if info["top_values"] else "-"
        col_table.add_row(
            col,
            f"{info['null_pct']:.1f}%",
            f"{info['unique_pct']:.1f}%",
            info["dtype"],
            top,
        )
    console.print(col_table)

    # Anomalies
    if any(anoms["columns"].values()) or anoms["global"]:
        anom_panel = rich.panel.Panel("🚨 Anomalies\n" + "\n".join(
            f"• {col}: {', '.join(issues)}" for col, issues in anoms["columns"].items() if issues
        ) + "\n".join(anoms["global"]), title="Anomalies", border_style="red")
        console.print(anom_panel)

    # Schema
    console.print(rich.panel.Panel(
        rich.syntax.Syntax(json.dumps(data["schema"], indent=2), "json"),
        title="📋 Inferred Schema",
    ))


def render_json(data: Dict[str, Any]) -> str:
    """JSON string."""
    return json.dumps(data, indent=2, default=str)


def render_html(data: Dict[str, Any]) -> str:
    """HTML report via Jinja."""
    with open(templates_dir / "report.html.jinja", "r") as f:
        template = Template(f.read())
    return template.render(data=data, version=__version__)