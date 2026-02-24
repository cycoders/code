from __future__ import annotations
import plotly.express as px
from pathlib import Path
import pandas as pd
from typing import List

from .tree_builder import SpanNode


def generate_waterfall_html(
    roots: List[SpanNode], output_dir: Path, trace_id: str, console=None
) -> Path:
    """Generate interactive Plotly waterfall HTML."""
    if console:
        console.print("[blue]Generating waterfall...[/]")

    rows = []

    def collect(node: SpanNode, path: str = ""):
        name = node.span.operationName
        full_path = f"{path}/{name}" if path else name
        rel_start = node.span.start_time_sec - _get_root_start(roots)
        rows.append(
            {
                "Path": full_path,
                "Operation": name,
                "Service": node.span.service,
                "Start (s)": rel_start,
                "End (s)": rel_start + node.span.duration_sec,
                "Duration (s)": node.span.duration_sec,
                "Self (s)": node.self_time,
                "Error": node.span.is_error,
            }
        )
        for child in node.children:
            collect(child, full_path)

    collect(roots[0] if roots else SpanNode())  # Assume single root

    if not rows:
        raise ValueError("No spans to visualize")

    df = pd.DataFrame(rows)
    fig = px.timeline(
        df,
        x_start="Start (s)",
        x_end="End (s)",
        y="Path",
        color="Service",
        hover_data=["Duration (s)", "Self (s)", "Error"],
        title=f"Trace {trace_id} - Waterfall",
    )
    fig.update_yaxes(autorange="reversed", title="Span Hierarchy")
    fig.update_xaxes(title="Time (s)")
    fig.update_layout(height=1200, showlegend=True)

    html_path = output_dir / f"{trace_id}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(html_path, include_plotlyjs="cdn")

    if console:
        console.print(f"[green]Waterfall saved: {html_path}[/]\nOpen in browser!")

    return html_path


def _get_root_start(roots: List[SpanNode]) -> float:
    return min(root.span.start_time_sec for root in roots)
