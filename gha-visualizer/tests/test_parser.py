import pytest
from pathlib import Path
from pytest import TempPathFactory

from gha_visualizer.parser import parse_workflow, extract_jobs
from gha_visualizer.models import Job


@pytest.fixture
def simple_workflow(tmp_path_factory: TempPathFactory) -> Path:
    wf_file = tmp_path_factory.mktemp(basename="wf") / "ci.yml"
    wf_file.write_text("""
name: CI
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: flake8 .
  test:
    needs: lint
    strategy:
      matrix:
        py: [3.11, 3.12]
    steps:
      - uses: actions/setup-python@v4
    """)
    return wf_file


def test_parse_workflow_valid(simple_workflow: Path):
    data = parse_workflow(simple_workflow)
    assert isinstance(data, dict)
    assert "jobs" in data
    assert data["jobs"]["lint"]["runs-on"] == "ubuntu-latest"


def test_parse_workflow_invalid_yaml(tmp_path: Path):
    invalid_file = tmp_path / "invalid.yml"
    invalid_file.write_text("invalid: yaml: here")
    with pytest.raises(ValueError, match="Invalid YAML"):
        parse_workflow(invalid_file)


def test_parse_workflow_no_jobs(tmp_path: Path):
    no_jobs_file = tmp_path / "nojobs.yml"
    no_jobs_file.write_text("name: Test")
    with pytest.raises(ValueError, match="No 'jobs' key"):
        parse_workflow(no_jobs_file)


def test_extract_jobs(simple_workflow: Path):
    data = parse_workflow(simple_workflow)
    jobs = extract_jobs(data)
    assert len(jobs) == 2
    assert jobs[0].name == "lint"
    assert jobs[0].needs == []
    assert len(jobs[0].steps) == 2
    assert jobs[1].name == "test"
    assert jobs[1].needs == ["lint"]
    assert jobs[1].strategy is not None