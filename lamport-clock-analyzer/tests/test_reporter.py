from lamport_clock_analyzer.reporter import report_violations

def test_report_no_violations(capsys):
    report_violations([])
    captured = capsys.readouterr()
    assert "No causality" in captured.out