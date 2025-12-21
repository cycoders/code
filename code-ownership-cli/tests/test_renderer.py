import io
from contextlib import redirect_stdout
from code_ownership_cli.renderer import render_stats
from code_ownership_cli.stats import OwnershipStats

def test_render_table(capsys):
    mock_stats = OwnershipStats(100, {"Alice": 60, "Bob": 40}, {}, [( "Alice", 60.0), ("Bob", 40.0)])
    render_stats(mock_stats, fmt="table")
    captured = capsys.readouterr()
    assert "Alice" in captured.out
    assert "60.0%" in captured.out


def test_render_json(capsys):
    mock_stats = OwnershipStats(100, {"Alice": 60}, {}, [])
    render_stats(mock_stats, fmt="json")
    captured = capsys.readouterr()
    assert '"total_lines": 100' in captured.out
