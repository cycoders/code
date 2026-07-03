from pathlib import Path
import tempfile
from exception_graph_cli.cli import app
from typer.testing import CliRunner

def test_run_on_tempdir():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.py"
        p.write_text("raise RuntimeError")
        runner = CliRunner()
        result = runner.invoke(app, [tmp, "--format", "mermaid"])
        assert result.exit_code == 0