from typing import Tuple

from .detector import is_confusable


def highlight_line(line: str) -> Tuple[str, int]:
    """
    Highlight confusables in a line with Rich markup.

    Returns (highlighted_markup, count).
    """
    parts: list[str] = []
    count = 0
    for char in line:
        if is_confusable(char):
            parts.append(f"[red bold]{char}[/red bold]")
            count += 1
        else:
            parts.append(char)
    highlighted = "".join(parts)
    return highlighted, count
