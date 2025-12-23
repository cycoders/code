import io
from unittest.mock import patch
from rich.console import Console
from import_profiler.reporter import report_console, _build_table


sample_data = {
    "total_startup_time": 0.01,
    "modules": {
        "__main__": {"inclusive": 0.01, "exclusive": 0.002, "deps": {"os": 0.008}},
        "os": {"inclusive": 0.008, "exclusive": 0.005, "deps": {}},
    },
}


@patch("rich.console.Console.print")
def test_console_report(mock_print):
    report_console(sample_data, threshold=0.1, tree=False, table=False, suggestions=False)
    mock_print.assert_called()


def test_table_build():
    table = _build_table(sample_data, 1.0)
    assert len(table.columns) == 4
    assert "os" in str(table)


@patch("sys.stdout", new_callable=io.StringIO)
def test_suggestions(mock_stdout):
    _print_suggestions(sample_data, 1.0)  # private but importable
    assert "✅" in mock_stdout.getvalue()
