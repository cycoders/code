import pytest
from datetime import datetime

from log_to_sequence.builder import build_spans
from log_to_sequence.models import LogEntry, Span


def test_build_simple():
    entries = [
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 0),
            trace_id="t1",
            span_id="s1",
            service="fe",
            name="root",
            duration_ms=100.0,
        ),
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 0, 1),
            trace_id="t1",
            span_id="s2",
            parent_span_id="s1",
            service="be",
            name="child",
            duration_ms=50.0,
        ),
    ]
    roots = build_spans(entries)
    assert len(roots) == 1
    root = roots[0]
    assert root.name == "root"
    assert len(root.children) == 1
    child = root.children[0]
    assert child.name == "child"
    assert child.service == "be"


def test_multiple_roots():
    entries = [
        LogEntry(span_id="r1", service="a", name="r1", trace_id="t", timestamp=datetime.now()),
        LogEntry(span_id="r2", service="b", name="r2", trace_id="t", timestamp=datetime.now()),
    ]
    roots = build_spans(entries)
    assert len(roots) == 2