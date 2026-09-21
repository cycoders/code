import tempfile
from pathlib import Path
from typosquat_auditor.scanner import scan_requirements

def test_detects_close_names():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('requests\nrequestes\n')
        path = f.name
    res = scan_requirements(path, 0.8)
    assert len(res) == 1
    Path(path).unlink()