import pytest
from pathlib import Path

from shell_auditor_cli.fixer import apply_fixes
from shell_auditor_cli.types import Issue


@pytest.fixture
def sample_issues():
    return [
        Issue("PERF001", 3, 0, "test", "medium", "grep err log"),
    ]


def test_apply_fixes(tmp_path: Path, sample_issues):
    script = Path(tmp_path / "test.sh")
    script.write_text("line1\nline2\ncat log | grep err\n")
    count = apply_fixes(script, sample_issues)
    assert count == 1
    new_content = script.read_text()
    assert "grep err log" in new_content


def test_no_fixes(tmp_path: Path):
    script = Path(tmp_path / "test.sh")
    script.write_text("no cat")
    issues = [Issue("SEC001", 1, 0, "no", "critical")]
    count = apply_fixes(script, issues)
    assert count == 0