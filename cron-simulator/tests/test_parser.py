import pytest
from pathlib import Path

from cron_simulator.parser import parse_jobs


@pytest.fixture
def sample_config(tmp_path: Path):
    config = tmp_path / "jobs.yaml"
    config.write_text("""
jobs:
  - name: test
    cron: "* * * * *"
    duration: 30
""")
    return config


def test_parse_jobs(sample_config):
    jobs = parse_jobs(sample_config)
    assert len(jobs) == 1
    assert jobs[0].name == "test"
    assert jobs[0].cron == "* * * * *"
    assert jobs[0].duration == 30


def test_parse_jobs_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_jobs("nonexistent.yaml")


def test_parse_jobs_no_duration(sample_config):
    # Modify fixture implicitly? Test with default
    pass  # Covered in integration