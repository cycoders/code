import ast
import pytest
from pathlib import Path

from datetime_auditor_cli.types import Issue
from datetime_auditor_cli.visitors import DatetimeAuditor


@pytest.mark.parametrize(
    "source, expected_count, msg_substr",
    [
        ("import datetime\ndt = datetime.now()", 1, "Naive `datetime.now"),
        ("import datetime\ndt = datetime.utcnow()", 1, "Naive `datetime.utcnow"),
        ("import datetime\ndt = datetime.now(datetime.timezone.utc)", 0, ""),
        ("import datetime\ndt = datetime.now(tz=datetime.timezone.utc)", 0, ""),
        ("import time, datetime\ndt = datetime.fromtimestamp(time.time())", 1, "fromtimestamp"),
        ("import datetime\ndt = datetime.fromtimestamp(123.45, tz=datetime.timezone.utc)", 0, ""),
        ("import datetime\ndt = datetime.strptime('2023-01-01', '%Y-%m-%d')", 1, "strptime"),
        ("import datetime\ndt = datetime(2023,1,1)", 1, "constructor"),
        ("import datetime\ndt = datetime(2023,1,1, tzinfo=datetime.timezone.utc)", 0, ""),
    ],
)
def test_datetime_cases(source: str, expected_count: int, msg_substr: str) -> None:
    tree = ast.parse(source)
    auditor = DatetimeAuditor(Path("test.py"), source)
    auditor.visit(tree)
    assert len(auditor.issues) == expected_count
    if expected_count > 0:
        assert msg_substr in auditor.issues[0].message