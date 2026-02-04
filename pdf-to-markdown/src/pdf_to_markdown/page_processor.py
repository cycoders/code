from typing import Any, List

import pdfplumber


def process_page(page: pdfplumber.page.Page, no_tables: bool = False) -> str:
    """Extract structured MD from page."""
    lines = page.extract_text_lines(layout=True) or []
    if not lines:
        return "# (Empty page)"

    # Median size for threshold
    sizes = [line.get("size", 12.0) for line in lines if line.get("size")]
    median_size = 12.0
    if sizes:
        sizes.sort()
        median_size = sizes[len(sizes) // 2]
    threshold = median_size * 1.2

    md_lines: List[str] = []
    for line in lines:
        text = line.get("text", "").strip()
        if not text or len(text) < 2:
            continue
        size = line.get("size", 12.0)
        fontname = str(line.get("fontname", "")).lower()
        is_bold = "bold" in fontname or "heavy" in fontname
        is_upper = text.isupper() and len(text) > 3

        if (
            size > threshold
            or (size > median_size and (is_bold or is_upper))
        ):
            rel_size = max(0.0, (size - median_size * 0.8) / max(1.0, threshold - median_size * 0.8))
            level = max(1, min(6, int(rel_size * 5) + 1))
            md_lines.append("#" * level + " " + text)
        elif text[0] in "•◦-*+" or text.startswith(("\u2022", "\u25cf")):
            bullet = text[0]
            rest = text[1:].strip()
            md_lines.append(f"- {rest}")
        else:
            md_lines.append(text)

    page_md = "\n\n".join(md_lines)

    if not no_tables:
        tables = page.extract_tables()
        if tables:
            page_md += "\n\n## Tables"
            for idx, table in enumerate(tables, 1):
                table_md = table_to_markdown(table)
                if table_md.strip():
                    page_md += f"\n\n### Table {idx}\n{table_md}"
    return page_md


def table_to_markdown(table: List[List[Any]]) -> str:
    """List-of-lists → MD table."""
    if not table:
        return ""
    num_cols = len(table[0]) if table[0] else 0
    if num_cols == 0:
        return ""

    # Header
    headers = [str(cell or "") for cell in table[0]]
    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * num_cols) + " |\n"

    # Rows
    for row in table[1:]:
        cells = [str(cell or "") for cell in row]
        # Pad short rows
        cells += [""] * (num_cols - len(cells))
        md += "| " + " | ".join(cells[:num_cols]) + " |\n"
    return md