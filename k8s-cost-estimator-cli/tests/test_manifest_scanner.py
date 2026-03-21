import pytest
from k8s_cost_estimator_cli.manifest_scanner import scan_manifests, SUPPORTED_KINDS
from pathlib import Path


@pytest.mark.parametrize("kind", SUPPORTED_KINDS)
def test_supported_kinds(tmp_path: Path, kind: str):
    manifest = tmp_path / "test.yaml"
    manifest.write_text(f"apiVersion: apps/v1\nkind: {kind}\nmetadata: {{name: test}}\nspec: {{}}")
    manifests = list(scan_manifests(tmp_path))
    assert len(manifests) == 1
    assert manifests[0]["kind"] == kind


def test_invalid_yaml_skipped(tmp_path: Path):
    (tmp_path / "invalid.yaml").write_text("invalid")
    assert list(scan_manifests(tmp_path)) == []
