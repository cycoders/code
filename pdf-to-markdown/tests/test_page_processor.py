import pytest
from unittest.mock import Mock, patch
from pdf_to_markdown.page_processor import process_page, table_to_markdown


@pytest.fixture
def mock_page_good(mock_page):
    mock_page.extract_text_lines.return_value = [
        {"text": "# Big Title", "size": 24.0, "fontname": "Arial-Bold"},
        {"text": "Normal para", "size": 12.0},
        {"text": "• Bullet item", "size": 12.0},
        {"text": "ALL CAPS", "size": 14.0},
    ]
    mock_page.extract_tables.return_value = []
    return mock_page


def test_process_page(mock_page_good):
    md = process_page(mock_page_good)
    assert "# Big Title" in md
    assert "- Bullet item" in md
    assert "ALL CAPS" in md  # upper
    assert "Normal para" in md


def test_table_to_markdown():
    table = [
        ["Name", "Value"],
        ["A", None],
        ["B", "1.23"],
    ]
    md = table_to_markdown(table)
    expected = """| Name | Value |
| --- | --- |
| A |  |
| B | 1.23 |
"""
    assert md == expected


def test_table_empty():
    assert table_to_markdown([]) == ""
    assert table_to_markdown([[]]) == ""


def test_process_no_tables(mock_page_good):
    mock_page_good.extract_tables.return_value = [[["h"]]]
    md = process_page(mock_page_good, no_tables=True)
    assert "## Tables" not in md