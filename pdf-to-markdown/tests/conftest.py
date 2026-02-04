import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_pdfplumber_open(monkeypatch):
    """Mock pdfplumber.open."""
    mock_pdf = MagicMock()
    mock_pdf.__len__.return_value = 5
    mock_pdf.pages = [Mock() for _ in range(5)]
    monkeypatch.setattr("pdf_to_markdown.converter.pdfplumber.open", lambda p: mock_pdf)
    return mock_pdf


@pytest.fixture
def mock_page():
    """Mock page."""
    page = Mock(spec=pdfplumber.page.Page)
    page.extract_text_lines.return_value = []
    page.extract_tables.return_value = []
    return page