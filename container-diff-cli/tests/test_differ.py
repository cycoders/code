import pytest
from container_diff_cli.differ import compute_diff
from container_diff_cli.types import LayerDelta


def test_compute_diff(mock_client):
    diff = compute_diff("img1", "img2")

    assert diff.size1 == 7200000
    assert diff.size_delta == 300000
    assert len(diff.layer_deltas) == 3
    assert any(ld.status == "added" for ld in diff.layer_deltas)
    assert any(ld.status == "same" for ld in diff.layer_deltas)


def test_config_delta(mock_client):
    diff = compute_diff("img1", "img2")
    assert "PATH" in diff.config_delta.changed_keys
    assert len(diff.config_delta.added_keys) >= 1
