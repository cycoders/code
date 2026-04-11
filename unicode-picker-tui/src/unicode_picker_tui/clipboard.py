"""Clipboard operations."""

import pyperclip


def copy(text: str) -> bool:
    """Copy to system clipboard."""
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException as e:
        print(f"Clipboard error: {e}", file=sys.stderr)
        return False
