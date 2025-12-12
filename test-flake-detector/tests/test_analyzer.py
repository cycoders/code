import pytest
from pathlib import Path

from test_flake_detector.analyzer import analyze_reports


@pytest.fixture
def sample_output_dir(tmp_path: Path) -> Path:
    out_dir = tmp_path / "flake"
    out_dir.mkdir()
    # Run 1: pass
    (out_dir / "run_001.txt").write_text("test.py::test_x PASSED\n")
    # Run 2: fail
    (out_dir / "run_002.txt").write_text("test.py::test_x FAILED\n")
    # Run 3: pass
    (out_dir / "run_003.txt").write_text("test.py::test_x PASSED\n")
    # Another stable
    for f in out_dir.glob("run_*.txt"):
        f.write_text(f.read_text() + "\ntest.py::test_stable PASSED\n")
    return out_dir


def test_analyze_flaky(sample_output_dir: Path) -> None:
    stats = analyze_reports(sample_output_dir)
    assert len(stats) == 2
    flaky = [s for s in stats if s["nodeid"].endswith("test_x")][0]
    assert flaky["flake_rate"] == pytest.approx(1 / 3)
    assert flaky["passes"] == 2
    assert flaky["fails"] == 1

    stable = [s for s in stats if s["nodeid"].endswith("test_stable")][0]
    assert stable["flake_rate"] == 0.0