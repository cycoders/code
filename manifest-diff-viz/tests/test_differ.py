import pytest
from manifest_diff_viz.differ import compute_diff, DEFAULT_IGNORES, compute_resource_diffs
from manifest_diff_viz.parser import load_manifests

@pytest.fixture
def simple_old():
    return {'spec': {'image': 'v1', 'replicas': 1}}

@pytest.fixture
def simple_new():
    return {'spec': {'image': 'v2', 'replicas': 2}}

def test_compute_diff_simple(simple_old, simple_new):
    changes = compute_diff(simple_old, simple_new, DEFAULT_IGNORES)
    assert len(changes) == 2
    assert changes[0]['type'] == 'modified'
    assert changes[0]['path'] == ['spec', 'image']

@pytest.fixture
def sample_manifests():
    before_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - image: nginx:v1
    """
    after_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    env: prod
spec:
  template:
    spec:
      containers:
      - image: nginx:v2
    """
    before_docs = list(yaml.safe_load_all(before_yaml))
    after_docs = list(yaml.safe_load_all(after_yaml))
    return before_docs, after_docs

def test_resource_diffs(sample_manifests):
    before, after = sample_manifests
    diffs = compute_resource_diffs(before, after, DEFAULT_IGNORES)
    assert len(diffs) == 1
    changes = diffs[list(diffs.keys())[0]]
    assert any(c['path'] == ['metadata', 'labels', 'env'] for c in changes)
    assert any(c['path'] == ['spec', 'template', 'spec', 'containers', 0, 'image'] for c in changes)

 def test_ignore(sample_manifests):
    before, after = sample_manifests
    diffs = compute_resource_diffs(before, after, DEFAULT_IGNORES + ['metadata.labels'])
    changes = diffs[list(diffs.keys())[0]]
    image_changes = [c for c in changes if c['path'][-1] == 'image']
    assert len(image_changes) == 1  # Still detects image change
    label_changes = [c for c in changes if '.labels.' in '.'.join(c['path'])]
    assert not label_changes  # Ignored