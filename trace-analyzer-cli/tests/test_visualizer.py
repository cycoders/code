import pytest
from pathlib import Path
from trace_analyzer_cli.visualizer import generate_waterfall_html
from trace_analyzer_cli.tree_builder import SpanNode
from trace_analyzer_cli.models import Span


@pytest.fixture
def sample_root():
    root = SpanNode(Span.model_validate(dict(traceID="1", spanID="r", parentSpanID=None, operationName="root", startTime=0, duration=1000000, tags={})))
    return [root]


def test_generate_waterfall(tmp_path: Path, sample_root):
    out_dir = tmp_path / "report"
    html_path = generate_waterfall_html(sample_root, out_dir, "test-trace", console=None)
    assert html_path.exists()
    assert html_path.suffix == ".html"
    assert "plotly" in html_path.read_text()
