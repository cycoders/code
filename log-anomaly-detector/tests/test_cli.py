import sys
from typer.testing import CliRunner

from log_anomaly_detector.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Batch anomaly detection" in result.stdout


def test_batch_no_args(sample_jsonl):
    result = runner.invoke(app, ["batch", str(sample_jsonl)])
    assert result.exit_code == 1
    assert "at least one field" in result.stdout.lower()

# More integration tests would mock parser etc.
