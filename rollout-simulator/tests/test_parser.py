import pytest
from pathlib import Path
import numpy as np  # type: ignore

from rollout_simulator.parser import parse_metrics, group_by_deploy
from rollout_simulator.types import DeployMetrics


def test_parse_metrics(sample_metrics: Path):
    entries = parse_metrics(sample_metrics)
    assert len(entries) == 30
    assert entries[0].deploy_id == "v1.0.0"
    assert 0.0 <= entries[0].error_rate <= 1.0


@pytest.mark.parametrize("bad_line", [b'{"bad":}', '[]', 'not json'])
def test_parse_invalid(tmp_path: Path, bad_line: str):
    p = tmp_path / "bad.jsonl"
    p.write_text(bad_line)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        parse_metrics(p)


def test_group_by_deploy(sample_metrics: Path):
    entries = parse_metrics(sample_metrics)
    deploys = group_by_deploy(entries)
    assert len(deploys) == 4
    assert deploys[0].deploy_id == "v1.0.0"
    assert abs(deploys[0].avg_error_rate - 0.008) < 0.001
    assert deploys[-1].last_ts > deploys[0].first_ts