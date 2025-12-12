import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from jinja2 import Template

def report_console(stats: List[Dict[str, Any]], threshold: float, console: Console) -> None:
    table = Table(title="Test Flake Analysis", show_header=True, header_style="bold magenta")
    table.add_column("Node ID", style="cyan", no_wrap=True)
    table.add_column("Passes", justify="right")
    table.add_column("Fails", justify="right")
    table.add_column("Skips", justify="right")
    table.add_column("Flake Rate", justify="right")

    for stat in stats[:25]:
        flake_pct = f"{stat['flake_rate']*100:.1f}%"
        row_style = "red bold" if stat["flake_rate"] > threshold else "green"
        table.add_row(
            stat["nodeid"][:65],
            str(stat["passes"]),
            str(stat["fails"]),
            str(stat["skips"]),
            f"[{row_style}]{flake_pct}[/{row_style}]",
        )

    console.print(table)

def report_json(stats: List[Dict[str, Any]], output_file: Path) -> None:
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with output_file.open("w") as f:
        json.dump(stats, f, indent=2, sort_keys=True)

def report_html(stats: List[Dict[str, Any]], threshold: float, output_file: Path) -> None:
    template_str = """
<!DOCTYPE html>
<html><head>
<title>Test Flake Report</title>
<style>
body{font-family:Arial;margin:40px}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:12px;text-align:left;}th{background:#f4f4f4;font-weight:600;}.flaky{background:#ffebee!important;color:#d32f2f;font-weight:700;}.pct{text-align:right;}
</style></head><body>
<h1>Test Flake Detector</h1>
<p>Generated: {{ now }} | Threshold: <strong>{{ threshold_pct }}</strong> | Flaky: <strong>{{ flaky_count }}</strong></p>
<table>
<tr><th>Node ID</th><th>Passes</th><th>Fails</th><th>Skips</th><th>Flake Rate</th></tr>
{% for s in stats %}
<tr {% if s.flake_rate > threshold %}class="flaky"{% endif %}>
<td>{{ s.nodeid }}</td><td>{{ s.passes }}</td><td>{{ s.fails }}</td><td>{{ s.skips }}</td><td class="pct">{{ "%.1f"|format(s.flake_rate * 100) }}%</td>
</tr>{% endfor %}</table>
</body></html>
    """
    t = Template(template_str)
    from datetime import datetime
    now = datetime.now().isoformat()
    flaky_count = sum(1 for s in stats if s["flake_rate"] > threshold)
    html = t.render(
        stats=stats,
        threshold=threshold,
        threshold_pct=f"{threshold*100:.1f}%",
        flaky_count=flaky_count,
        now=now,
    )
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text(html)