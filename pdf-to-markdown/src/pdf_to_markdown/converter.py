from __future__ import annotations
import pdfplumber
from typing import Iterator, List, Optional

from .page_processor import process_page


def get_page_indices(pdf_path: str, pages_str: Optional[str] = None) -> List[int]:
    """Parse --pages to 0-based indices."""
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
    if pages_str is None:
        return list(range(num_pages))
    indices: set[int] = set()
    for part in pages_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            start = 1 if not left else int(left)
            end = num_pages if not right else int(right)
            indices.update(range(start - 1, end))
        else:
            indices.add(int(part) - 1)
    return sorted(i for i in indices if 0 <= i < num_pages)


def iter_pages_md(
    pdf_path: str, pages: Optional[str] = None, no_tables: bool = False
) -> Iterator[str]:
    """Yield MD for each page (streaming)."""
    indices = get_page_indices(pdf_path, pages)
    with pdfplumber.open(pdf_path) as pdf:
        for idx in indices:
            page = pdf.pages[idx]
            yield process_page(page, no_tables)


def convert_pdf_to_md(
    pdf_path: str, pages: Optional[str] = None, no_tables: bool = False
) -> str:
    """Full doc to MD str."""
    md_parts = list(iter_pages_md(pdf_path, pages, no_tables))
    return "\n\n--- Page Break ---\n\n".join(md_parts)