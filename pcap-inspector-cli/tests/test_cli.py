import pytest
from click.testing import CliRunner
from pcap_inspector_cli.cli import app

runner = CliRunner()


def test_inspect_help():
    result = runner.invoke(app, ["inspect", "--help"])
    assert result.exit_code == 0

# More integration tests would mock analyzer, but basic smoke


class TestCLI:
    def test_version(self, sample_pcap):
        # Callback version not direct, but via --version global? Typer no global
        pass

    def test_invalid_file(self):
        result = runner.invoke(app, ["inspect", "nonexistent.pcap"])
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_json_output(self, sample_pcap):
        result = runner.invoke(app, ["inspect", str(sample_pcap), "--json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.stdout)
        assert "packets" in data
        assert data["packets"] == 5