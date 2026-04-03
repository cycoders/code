import pytest
from pathlib import Path

from datetime_auditor_cli.auditor import audit_directory


@pytest.mark.parametrize(
    "files, expected_issues",
    [
        ([], 0),
        ([("good.py", "import datetime\nprint(datetime.now(tz=None))")], 0),
        ([("bad.py", "import datetime\ndt = datetime.now()")], 1),
    ],
)
def test_audit_directory(tmp_path: Path, files: list[tuple[str, str]], expected_issues: int) -> None:
    for fname, content in files:
        (tmp_path / fname).write_text(content)
    issues = audit_directory(tmp_path)
    assert len(issues) == expected_issues


def test_skips_invalid_syntax(tmp_path: Path) -> None:
    (tmp_path / "invalid.py").write_text("def x: pass")
    issues = audit_directory(tmp_path)
    assert len(issues) == 0