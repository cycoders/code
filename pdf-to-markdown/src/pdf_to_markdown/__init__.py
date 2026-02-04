'''High-fidelity PDF to Markdown converter.'''

__version__ = "0.1.0"


from .converter import (
    convert_pdf_to_md,
    iter_pages_md,
    get_page_indices,
)
from .page_processor import (
    process_page,
    table_to_markdown,
)

__all__ = [
    "convert_pdf_to_md",
    "iter_pages_md",
    "get_page_indices",
    "process_page",
    "table_to_markdown",
]