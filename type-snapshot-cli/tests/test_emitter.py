import tempfile
from pathlib import Path
from type_snapshot_cli.emitter import emit_patch

def test_emit_patch():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.patch"
        emit_patch({"mod.fn:x": "int"}, out)
        assert "int" in out.read_text()