from typing import Dict, Any, List, Tuple
import hashlib
import jinja2
from rich.console import Console
from rich.table import Table
from startup_profiler.profiler import ImportProfiler  # noqa


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: 'Segoe UI', monospace; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f4f4f4; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        svg { border: 1px solid #ddd; max-width: 100%; height: auto; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div>{{ svg|safe }}</div>
    <table>
        <thead>
            <tr>
                <th>Module</th>
                <th>Total (ms)</th>
                <th>Self (ms)</th>
                <th>Size (KB)</th>
                <th>% Total</th>
            </tr>
        </thead>
        <tbody>
            {% for mod, t in timings[:50] %}
            <tr>
                <td>{{ mod }}</td>
                <td>{{ "%.1f"|format(t.total * 1000) }}</td>
                <td>{{ "%.1f"|format(t.self * 1000) }}</td>
                <td>{{ "%.1f"|format(t.size) }}</td>
                <td>{{ "%.1f"|format((t.total / meta.total_time * 100) if meta.total_time else 0) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


def render_table(timings: Dict[str, Any], console: Console) -> None:
    table = Table(title="Import Timings (Top 20, sorted by total)", show_header=True, header_style="bold magenta")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Total (ms)", justify="right")
    table.add_column("Self (ms)", justify="right")
    table.add_column("Size (KB)", justify="right")
    table.add_column("% Total", justify="right")
    total_all = sum(t.get("total", 0) for t in timings.values()) if timings else 0
    if "_meta" in timings:
        total_all = timings["_meta"].get("total_time", total_all)
    sorted_mods = sorted(
        [k for k in timings if k != "_meta"], key=lambda k: timings[k].get("total", 0), reverse=True
    )[:20]
    for mod in sorted_mods:
        t = timings[mod]
        pct = (t["total"] / total_all * 100) if total_all else 0
        table.add_row(mod, f"{t['total']*1000:.1f}", f"{t['self']*1000:.1f}", f"{t['size']:.1f}", f"{pct:.1f}%")
    console.print(table)


def render_flamegraph_svg(timings: Dict[str, Any], width: int = 1400, height_per_row: int = 25, min_ms: float = 1.0) -> str:
    items: List[Tuple[str, Dict[str, Any]]] = []
    for k, v in timings.items():
        if k == "_meta" or v.get("total", 0) * 1000 < min_ms:
            continue
        items.append((k, v))
    items.sort(key=lambda x: x[1]["total"], reverse=True)
    n_rows = len(items)
    if n_rows == 0:
        return '<svg width="400" height="100"><text x="10" y="50">No data</text></svg>'
    height = 50 + n_rows * height_per_row
    max_total = items[0][1]["total"]
    label_width = 320
    bar_max_w = width - label_width - 20
    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#f8f9fa"/>',
    ]
    for i, (name, data) in enumerate(items):
        frac = data["total"] / max_total
        bar_w = min(frac * bar_max_w, bar_max_w)
        y = 40 + i * height_per_row
        h = hashlib.md5(name.encode())
        hue = int(h.hexdigest(), 16) % 359
        color = f"hsl({hue}, 65%, 60%)"
        label = f"{name.split('.')[-1]} ({data['total']*1000:.0f}ms s:{data['self']*1000:.0f}ms)"
        svg_parts += [
            f'<rect x="{label_width}" y="{y}" width="{bar_w}" height="{height_per_row-2}" rx="3" fill="{color}" stroke="#eee" stroke-width="0.5"/>',
            f'<text x="10" y="{y + height_per_row//2 + 5}" font-size="13" font-family="\'Segoe UI Mono\', monospace" fill="#333">{label}</text>',
        ]
    svg_parts.append("</svg>")
    return "".join(svg_parts)


def render_html_report(timings: Dict[str, Any], title: str = "Startup Profiler Report") -> str:
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = env.from_string(HTML_TEMPLATE)
    sorted_timings = sorted(
        [(k, v) for k, v in timings.items() if k != "_meta"], key=lambda x: x[1].get("total", 0), reverse=True
    )[:50]
    meta = timings.get("_meta", {"total_time": 0})
    svg = render_flamegraph_svg(timings)
    return template.render(title=title, timings=sorted_timings, svg=svg, meta=meta)
