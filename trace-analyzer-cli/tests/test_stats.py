import pytest
from unittest.mock import Mock
from trace_analyzer_cli.stats import get_top_bottlenecks, print_trace_stats
from trace_analyzer_cli.tree_builder import SpanNode
from trace_analyzer_cli.models import Span


@pytest.fixture
def sample_roots():
    root = SpanNode(Span.model_validate({"traceID":"1","spanID":"r","parentSpanID":None,"operationName":"root","startTime":0,"duration":1000000,"tags":{"service.name":"s1"}}))
    child1 = SpanNode(Span.model_validate({"traceID":"1","spanID":"c1","parentSpanID":"r","operationName":"slow","startTime":0,"duration":800000,"tags":{"service.name":"s2","error":"true"}}))
    root.children = [child1]
    return [root]


def test_top_bottlenecks(sample_roots, monkeypatch):
    monkeypatch.setattr("trace_analyzer_cli.stats.console", Mock())
    tops = get_top_bottlenecks(sample_roots, top_n=5)
    assert len(tops) == 2
    assert tops[0].span.operationName == "root"


def test_print_stats(sample_roots, monkeypatch):
    mock_print = Mock()
    monkeypatch.setattr("rich.console.Console.print", mock_print)
    monkeypatch.setattr("trace_analyzer_cli.stats.console", Mock())
    print_trace_stats(sample_roots)
    mock_print.assert_called()
