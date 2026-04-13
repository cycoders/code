from pathlib import Path

from .cli import app

if __name__ == "__main__":
    import sys
    app(prog_name="disk-usage-tui")