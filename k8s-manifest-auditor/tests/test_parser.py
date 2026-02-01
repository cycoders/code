import yaml
from pathlib import Path

from k8s_manifest_auditor.parser import parse_manifests


def test_parse_manifests(examples_dir: Path):
    manifests = parse_manifests(examples_dir)
    assert len(manifests) >= 2
    assert manifests[0]["kind"] == "Deployment"


def test_invalid_yaml():
    bad_path = Path("nonexistent/bad.yaml")
    manifests = parse_manifests(bad_path.parent)
    assert len(manifests) == 0  # No files
