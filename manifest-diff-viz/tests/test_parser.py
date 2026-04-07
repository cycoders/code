import pytest
from pathlib import Path
import yaml
from manifest_diff_viz.parser import load_manifests, get_resource_key

@pytest.fixture
def sample_yaml_str():
    return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: default
---
apiVersion: v1
kind: Service
metadata:
  name: app-svc
  namespace: default
    """

@pytest.fixture
def sample_file(tmp_path: Path):
    p = tmp_path / "test.yaml"
    p.write_text(sample_yaml_str())
    return p

def test_load_single_file(sample_file):
    docs = load_manifests([sample_file])
    assert len(docs) == 2
    assert docs[0]['kind'] == 'Deployment'

def test_load_dir(tmp_path: Path):
    (tmp_path / "dir" / "a.yaml").write_text(sample_yaml_str())
    docs = load_manifests([tmp_path / "dir"])
    assert len(docs) == 2

def test_get_resource_key():
    doc = yaml.safe_load("""
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: prod
  name: web
    """)
    key = get_resource_key(doc)
    assert key == "apps/v1-Deployment-prod-web"

def test_invalid_yaml(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("invalid: yaml")
    with pytest.raises(ValueError):
        load_manifests([p])