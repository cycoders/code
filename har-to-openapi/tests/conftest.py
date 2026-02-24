import pytest
from pathlib import Path
@pytest.fixture
def sample_har_path():
    return Path(__file__).parent / "fixtures" / "sample.har"
