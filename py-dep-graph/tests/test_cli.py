import pytest
from click.testing import CliRunner
from py_dep_graph.cli import app


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.stdout

    def test_graph_simple(self, runner, simple_proj):
        result = runner.invoke(app, ["graph", str(simple_proj)])
        assert result.exit_code == 0
        assert "2 modules" in result.stdout
        assert "main" in result.stdout
        assert "utils" in result.stdout

    def test_cycles(self, runner, cycle_proj):
        result = runner.invoke(app, ["cycles", str(cycle_proj)])
        assert result.exit_code == 0
        assert "Found 1 cycle" in result.stdout

    @pytest.mark.parametrize("fmt", ["tree", "dot"])
    def test_formats(self, runner, simple_proj, fmt):
        result = runner.invoke(app, ["graph", str(simple_proj), "--format", fmt])
        assert result.exit_code == 0
