import pytest
from datetime import datetime

from log_to_sequence.renderer import render_mermaid
from log_to_sequence.models import Span
from log_to_sequence.utils import get_service_alias


def test_render_simple():
    root = Span(
        span_id="1",
        service="fe",
        name="handle",
        duration_ms=100.0,
        start_ts=datetime.now(),
        children=[
            Span(
                span_id="2",
                service="be",
                name="process",
                duration_ms=50.0,
                start_ts=datetime.now(),
                children=[],
            )
        ],
    )
    mermaid = render_mermaid([root], {})
    expected = """sequenceDiagram
    participant be as be
    participant fe as fe
    activate fe
    Note over fe: handle
    fe ->> be: process
    activate be
    Note over be: 50ms
    deactivate be
    be -->> fe
    Note over fe: 100ms
    deactivate fe"""
    assert expected.replace("\n", " ").strip() in mermaid.replace("\n", " ").strip()


def test_no_spans():
    mermaid = render_mermaid([], {})
    assert "No spans" in mermaid