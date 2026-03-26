import pytest
from click.testing import CliRunner
from typer.testing import CliRunner as TyperRunner

from yaml_dereferencer_cli.cli import app

runner = TyperRunner()

SIMPLE_PATH = Path(__file__).parent / "data" / "simple.yaml"

@pytest.fixture
def simple_yaml_file(tmp_path):
    p = tmp_path / "test.yaml"
    p.write_text(SIMPLE)
    return p

class TestCLI:
    def test_resolve(self, simple_yaml_file, tmp_path):
        out = tmp_path / "out.yaml"
        result = runner.invoke(app, ["resolve", str(simple_yaml_file), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "*x" not in out.read_text()

    def test_diff(self, simple_yaml_file):
        result = runner.invoke(app, ["diff", str(simple_yaml_file)])
        assert result.exit_code == 0
        assert result.stdout

    def test_validate_valid(self, simple_yaml_file):
        result = runner.invoke(app, ["validate", str(simple_yaml_file)])
        assert result.exit_code == 0

    def test_stats(self, simple_yaml_file):
        result = runner.invoke(app, ["stats", str(simple_yaml_file)])
        assert result.exit_code == 0
        assert "shared_anchors" in result.stdout

    def test_error(self):
        result = runner.invoke(app, ["validate", "nonexistent.yaml"])
        assert result.exit_code == 1
