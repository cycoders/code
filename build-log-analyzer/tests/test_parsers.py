import pytest
from pathlib import Path
from build_log_analyzer.parsers import parse_log, detect_parser
from build_log_analyzer.models import LogSummary


@pytest.fixture
def docker_log(tmp_path: Path):
    log_file = tmp_path / "docker.log"
    log_file.write_text(
        "Step 1/3 : FROM node:latest (1.0s)\n"
        "---> Using cache\n"
        "Step 2/3 : COPY . /app (0.5s)\n"
        "error: copy failed\n"
        "Step 3/3 : RUN npm ci (10.2s)\n"
    )
    return log_file


@pytest.fixture
def cargo_log(tmp_path: Path):
    log_file = tmp_path / "cargo.log"
    log_file.write_text("Finished release [optimized] target(s) in 23.4s\nerror[E0425]")
    return log_file


@pytest.fixture
def npm_log(tmp_path: Path):
    log_file = tmp_path / "npm.log"
    log_file.write_text("added 150 packages in 12.3s\nWARN deprecated")
    return log_file


def test_detect_parser():
    assert detect_parser("docker build") == "docker"
    assert detect_parser("cargo build") == "cargo"
    assert detect_parser("npm install") == "npm"
    assert detect_parser("pip install") == "pip"
    assert detect_parser("random text") == "generic"


def test_parse_docker(docker_log: Path):
    summary = parse_log(docker_log)
    assert summary.parser_used == "docker"
    assert len(summary.steps) == 3
    assert summary.total_duration == 11.7
    assert summary.total_errors == 1
    assert any("COPY" in s.name for s in summary.steps)


def test_parse_cargo(cargo_log: Path):
    summary = parse_log(cargo_log)
    assert summary.parser_used == "cargo"
    assert summary.total_duration == 23.4
    assert summary.total_errors == 1
    assert len(summary.steps) == 1


def test_parse_npm(npm_log: Path):
    summary = parse_log(npm_log)
    assert summary.parser_used == "npm"
    assert summary.total_duration == 12.3
    assert summary.total_warnings == 1


def test_generic_errors(tmp_path: Path):
    log_file = tmp_path / "generic.log"
    log_file.write_text("Build failed ERROR: boom\nWARN: slow\nTook 5m 30s")
    summary = parse_log(log_file)
    assert summary.total_errors == 1
    assert summary.total_warnings == 1
    assert summary.total_duration == 330.0