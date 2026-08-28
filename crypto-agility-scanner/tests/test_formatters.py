from crypto_agility_scanner.formatters import render
from rich.console import Console

def test_render_text():
    console = Console()
    render([], "text", None, console)  # smoke test