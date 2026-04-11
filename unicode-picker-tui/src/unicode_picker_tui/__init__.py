__version__ = "0.1.0"

__title__ = "unicode-picker-tui"
__summary__ = "Interactive TUI for browsing, fuzzy-searching, and copying Unicode characters"
__uri__ = "https://github.com/cycoders/code/tree/main/unicode-picker-tui"

try:
    from .main import run
except ImportError:
    pass