import pytest
from pathlib import Path

from test_flake_detector.parser import parse_run


@pytest.mark.parametrize(
    "line,expected_nodeid",
    [
        ("test.py::test_pass PASSED", "test.py::test_pass"),
        ("test.py::test_param[foo-bar] FAILED", "test.py::test_param[foo-bar]"),
        ("pkg/mod.py::TestCls::test_mth SKIPPED [50%]", "pkg/mod.py::TestCls::test_mth"),
        ("test.py::test_xfailed XFAILED", "test.py::test_xfailed"),
    ],
)
def test_parse_patterns(tmp_path: Path, line: str, expected_nodeid: str) -> None:
    out_file = tmp_path / "run.txt"
    out_file.write_text(line + "\n")
    results = parse_run(out_file)
    assert list(results.keys())[0] == expected_nodeid
    assert results[expected_nodeid] == ["PASSED" if "PASSED" in line else line.split()[-1].rstrip("[]%")]