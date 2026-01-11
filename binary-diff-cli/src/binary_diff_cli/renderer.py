from typing import List

Markup = str


def highlight_hex(hex_str: str, diff_pos: List[int]) -> Markup:
    """
    Highlight changed bytes in hex string with Rich markup.

    e.g. '00 11 ff' -> '[bold red on yellow]ff[/]'
    """
    parts = hex_str.split(" ")
    highlighted_parts = []
    for i, part in enumerate(parts):
        if i in diff_pos:
            highlighted_parts.append(f"[bold red on yellow]{part}[/]" )
        else:
            highlighted_parts.append(part)
    return " ".join(highlighted_parts)
