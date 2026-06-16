import tempfile, os
from rbac_visualizer.parser import load_from_manifests

def test_manifest_loading():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'rbac.yaml')
        open(p, 'w').write('kind: ClusterRole\nmetadata: {name: x}\n')
        objs = load_from_manifests(tmp)
        assert len(objs) == 1