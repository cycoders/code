from rich.console import Console
from heap_snapshot_diff.reporter import render_table

def test_render(capsys):
    console = Console()
    render_table([{"type": "list", "growth": 0.5, "delta_bytes": 1024}], console)
    assert "list" in capsys.readouterr().out