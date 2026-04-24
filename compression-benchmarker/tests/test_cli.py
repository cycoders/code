import pytest
from pathlib import Path
from typer.testing import CliRunner

from compression_benchmarker.cli import app

runner = CliRunner()


@pytest.fixture
def sample_file(tmp_path: Path):
    f = tmp_path / "test.txt"
    f.write_bytes(b"hello" * 10000)
    return str(f)


def test_bench_file(sample_file):
    result = runner.invoke(app, ["bench", sample_file, "--algo", "gzip,lz4", "--levels", "6"])
    assert result.exit_code == 0
    assert "%" in result.stdout
    assert "gzip" in result.stdout
    assert "MB/s" in result.stdout


def test_stdin(sample_file):
    with open(sample_file, "rb") as f:
        result = runner.invoke(app, ["bench", "-"], stdin=f)
    assert result.exit_code == 0


def test_invalid_file():
    result = runner.invoke(app, ["bench", "/nonexistent.txt"])
    assert result.exit_code != 0
    assert "not a file" in result.stdout


def test_invalid_algo():
    result = runner.invoke(app, ["bench", "tests/nonexistent.txt", "--algo", "foo"])
    assert result.exit_code != 0
    assert "Unknown compressor" in result.stdout
