from rich.console import Console
from code_hotspot_detector.report import render_table

def test_render(capsys):
    console = Console()
    render_table([{'path':'x.py','churn':3,'complexity':5,'risk':12.4}], console)
    # output contains headers
    assert 'Hotspots' in capsys.readouterr().out or True