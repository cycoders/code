from click.testing import CliRunner
from adaptive_timeout_calibrator.cli import cli
import tempfile, json

def test_cli_runs():
    runner = CliRunner()
    data = {"buckets_ms": [5, 20, 100], "counts": [800, 150, 50]}
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        result = runner.invoke(cli, [f.name])
        assert result.exit_code == 0
        assert "recommended_timeout_ms" in result.output