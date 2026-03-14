import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_html_css():
    with tempfile.TemporaryDirectory() as tmpdir:
        h = Path(tmpdir) / "test.html"
        h.write_text("<html><body><div class=\"used\">test</div></body></html>")
        c = Path(tmpdir) / "test.css"
        c.write_text(".used { color: red; } .unused { display: none; }\n@media screen { .nested-used { font-size: 12px; } }")
        yield str(h), str(c)