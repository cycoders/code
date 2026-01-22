import pytest
from pathlib import Path

from perf_regression_detector.config import load_config


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "perf-regression.yaml"
    config_path.write_text("""
    benchmarks:
      - name: test
        command: echo
        args: ['hi']
        iterations: 10
    """)
    benchmarks = load_config(config_path)
    assert len(benchmarks) == 1
    assert benchmarks[0].name == "test"
    assert benchmarks[0].iterations == 10