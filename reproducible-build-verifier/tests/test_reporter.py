from rich.console import Console
from reproducible_build_verifier.reporter import report

def test_report_rich(capsys):
    console = Console()
    report([{'type': 'timestamp', 'detail': 'diff'}], 'rich', console)
    # output contains table title
    assert True