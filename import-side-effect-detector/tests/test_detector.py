from pathlib import Path
import tempfile
from import_side_effect_detector.detector import find_side_effects

def test_detects_requests_call():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("import requests\nrequests.get('https://example.com')")
        effects = find_side_effects(tmp)
        assert len(effects) == 1
        assert effects[0].kind == "network_or_subprocess"

def test_ignores_safe_imports():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "good.py"
        p.write_text("import os\nprint(os.getcwd())")
        assert find_side_effects(tmp) == []

def test_handles_syntax_error():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "broken.py").write_text("import")
        assert find_side_effects(tmp) == []

def test_multiple_files():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "a.py").write_text("import socket\nsocket.socket()")
        (Path(tmp) / "b.py").write_text("import json\nprint(json.dumps({}))")
        assert len(find_side_effects(tmp)) == 1

def test_line_numbers():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "x.py"
        p.write_text("\n\nimport httpx\nhttpx.get('url')")
        effects = find_side_effects(tmp)
        assert effects[0].line == 4
