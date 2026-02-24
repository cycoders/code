import json
from pathlib import Path
import pytest
from trace_analyzer_cli.parser import parse_file, build_span_trees
from trace_analyzer_cli.models import Span
from trace_analyzer_cli.tree_builder import SpanNode


@pytest.fixture
def sample_json_path(tmp_path: Path):
    json_path = tmp_path / "sample.json"
    json_path.write_text(json.dumps([{"traceID": "1", "spans": [{"traceID": "1", "spanID": "root", "parentSpanID": None, "operationName": "root", "startTime": 0, "duration": 1000, "tags": {"service.name": "s1"}}, {"traceID": "1", "spanID": "child", "parentSpanID": "root", "operationName": "child", "startTime": 100, "duration": 400, "tags": {"service.name": "s2"}}]}]))
    return json_path


def test_parse_file(sample_json_path):
    trees = parse_file(sample_json_path, None)
    assert len(trees) == 1
    tid = next(iter(trees))
    assert len(trees[tid]) == 1  # one root
    root = trees[tid][0]
    assert len(root.children) == 1
    assert root.children[0].span.spanID == "child"
    assert root.self_time == pytest.approx(0.6, rel=1e-1)  # 1.0 - 0.4


def test_build_trees_self_time():
    spans = [
        Span.model_validate({"traceID": "1", "spanID": "r", "parentSpanID": None, "operationName": "r", "startTime": 0, "duration": 1000000, "tags": {}}),
        Span.model_validate({"traceID": "1", "spanID": "c", "parentSpanID": "r", "operationName": "c", "startTime": 0, "duration": 400000, "tags": {}}),
    ]
    roots = build_span_trees(spans)
    assert len(roots) == 1
    assert roots[0].self_time == pytest.approx(0.6)


def test_no_spans():
    empty_json = Path("nonexistent")
    with pytest.raises(ValueError, match="Empty"):
        parse_file(empty_json, None)
