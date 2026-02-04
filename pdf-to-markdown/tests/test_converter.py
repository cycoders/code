import pytest
from pdf_to_markdown.converter import get_page_indices, iter_pages_md, convert_pdf_to_md


@pytest.mark.parametrize(
    "pages_str,expected",
    [
        (None, [0, 1, 2, 3, 4]),
        ("1-3", [0, 1, 2]),
        ("3-5,1", [0, 2, 3, 4]),
        ("6-", []),
        ("", [0, 1, 2, 3, 4]),
    ],
)
def test_get_page_indices(mock_pdfplumber_open, pages_str, expected):
    indices = get_page_indices("fake.pdf", pages_str)
    assert indices == expected


def test_iter_pages_md(mock_pdfplumber_open, mock_page):
    for i in range(5):
        mock_pdfplumber_open.pages[i] = mock_page
    pages_md = list(iter_pages_md("fake.pdf"))
    assert len(pages_md) == 5
    assert all("Empty" in p for p in pages_md)


def test_convert_pdf_to_md(mock_pdfplumber_open, mock_page):
    for i in range(5):
        mock_pdfplumber_open.pages[i] = mock_page
    md = convert_pdf_to_md("fake.pdf")
    assert "--- Page Break ---" in md
    assert len(md.split("---")) == 6  # 5 pages + ends