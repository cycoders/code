import pytest
from config_drift_detector.compare import run

def test_basic_diff(tmp_path):
    base = tmp_path / 'base.yaml'
    base.write_text('port: 8080')
    tgt = tmp_path / 'tgt.yaml'
    tgt.write_text('port: 9090')
    res = run(str(base), [str(tgt)])
    assert len(res) == 1