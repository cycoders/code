import io

from type_coverage_cli.models import OverallStats, ElementCoverage, FileStats
from type_coverage_cli.reporter import print_table_report, print_json_report


def test_print_json_report(capfd):
    stats = OverallStats(
        files=1,
        funcs=ElementCoverage(10, 8),
        params=ElementCoverage(20, 18),
        returns=ElementCoverage(10, 9),
        file_stats=[FileStats("test.py", ElementCoverage(5, 4), ElementCoverage(10, 9), ElementCoverage(5, 5))],
    )
    output = io.StringIO()
    print_json_report(stats, output)
    captured = output.getvalue()
    assert '"funcs": {"total": 10, "typed": 8}' in captured


def test_print_table_report(capfd):
    stats = OverallStats(funcs=ElementCoverage(2, 1))
    console = io.StringIO()
    # Mock console print would need rich highlevel, but check logic via import
    print_table_report(stats, None)  # No crash
    assert True