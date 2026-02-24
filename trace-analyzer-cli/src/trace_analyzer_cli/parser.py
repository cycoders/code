from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import rich.console

from .models import Span, SpanNode


def parse_file(file_path: Path, console: rich.console.Console) -> Dict[str, List[SpanNode]]:
    """Parse Jaeger/OTel JSON trace file(s). Supports single/multi-trace."""
    with file_path.open("r") as f:
        data = json.load(f)

    # Handle Jaeger formats: list[trace] or dict{data: list[trace]}
    if isinstance(data, dict) and "data" in data:
        traces_data = data["data"]
    elif isinstance(data, list):
        traces_data = data
    else:
        traces_data = [data]

    trace_spans: Dict[str, List[Span]] = {}
    for trace_obj in traces_data:
        if isinstance(trace_obj, dict) and "spans" in trace_obj:
            tid = trace_obj.get("traceID", "unknown")
            spans = [Span.model_validate(s) for s in trace_obj["spans"]]
            trace_spans[tid] = spans
        elif isinstance(trace_obj, list):
            # Raw spans list, use first traceID
            if trace_obj:
                tid = trace_obj[0].get("traceID", "unknown")
                trace_spans[tid] = [Span.model_validate(s) for s in trace_obj]

    trees: Dict[str, List[SpanNode]] = {}
    for tid, spans in trace_spans.items():
        trees[tid] = build_span_trees(spans)

    if not trees:
        console.print("[red]No valid spans found.[/]")
        raise ValueError("Empty trace file")

    return trees


def build_span_trees(spans: List[Span]) -> List[SpanNode]:
    """Build hierarchical SpanNode trees from flat spans."""
    span_map: Dict[str, SpanNode] = {span.spanID: SpanNode(span) for span in spans}

    for node in list(span_map.values()):
        parent_id = node.span.parentSpanID
        if parent_id and parent_id in span_map:
            span_map[parent_id].children.append(node)

    roots = [node for node in span_map.values() if node.span.parentSpanID is None]

    # Compute exclusive self_times bottom-up
    for root in roots:
        _compute_exclusive_times(root)

    return roots


def _compute_exclusive_times(node: SpanNode) -> float:
    """Recursively compute exclusive self time: max(0, dur - sum(child dur))."""
    child_total = sum(_compute_exclusive_times(child) for child in node.children)
    node.self_time = max(0.0, node.span.duration_sec - child_total)
    return node.span.duration_sec
