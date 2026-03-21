import pytest
import yaml
from pathlib import Path

@pytest.fixture
def sample_deployment():
    return yaml.safe_load(Path("tests/fixtures/deployment.yaml").read_text())

@pytest.fixture
def sample_daemonset():
    return yaml.safe_load(Path("tests/fixtures/daemonset.yaml").read_text())
