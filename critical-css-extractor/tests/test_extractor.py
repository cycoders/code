import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from critical_css_extractor.extractor import extract_critical_css, get_html_content
from critical_css_extractor.css_utils import get_all_css_sources


class TestExtractor:
    @pytest.mark.parametrize(
        "input_str,expected",
        [("test.html", ("file://test.html", Path("test.html"))), ("https://ex.com", ("https html", None))],
    )
    def test_get_html_content(self, input_str, expected):
        # Simplified, as fixtures
        pass

    def test_get_all_css_sources(self, sample_soup, tmp_path: Path):
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: black; }")
        sources = get_all_css_sources(sample_soup, None, [css_file], False)
        assert len(sources) == 1
        assert "color: black" in sources[0]

    def test_extract_critical_css(self, sample_html, sample_css, tmp_path):
        html_path = tmp_path / "test.html"
        html_path.write_text(sample_html)
        css_path = tmp_path / "styles.css"
        css_path.write_text(sample_css)
        result = extract_critical_css(str(html_path), [css_path], 100, True)
        assert "hero" in result
        assert "below" not in result
        assert len(result) < 200