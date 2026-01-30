from collections import defaultdict
from typing import List

import log_to_sequence.models as models


def build_spans(entries: List[models.LogEntry]) -> List[models.Span]:
    if not entries:
        return []

    span_map: Dict[str, models.Span] = {}
    parent_to_children: Dict[str, List[str]] = defaultdict(list)

    for entry in entries:
        span = models.Span(
            span_id=entry.span_id,
            service=entry.service,
            name=entry.name,
            duration_ms=entry.duration_ms,
            start_ts=entry.timestamp,
            children=[],
        )
        span_map[entry.span_id] = span
        if entry.parent_span_id:
            parent_to_children[entry.parent_span_id].append(entry.span_id)

    # Link children
    for parent_id, child_ids in parent_to_children.items():
        if parent_id in span_map:
            parent = span_map[parent_id]
            parent.children = [span_map[cid] for cid in child_ids if cid in span_map]

    # Find roots: spans not referenced as children
    all_children = set(cid for cids in parent_to_children.values() for cid in cids)
    roots = [span for span in span_map.values() if span.span_id not in all_children]

    # Sort children recursively by start_ts
    def sort_recursively(span: models.Span) -> None:
        span.children.sort(key=lambda c: c.start_ts)
        for child in span.children:
            sort_recursively(child)

    for root in roots:
        sort_recursively(root)

    return roots