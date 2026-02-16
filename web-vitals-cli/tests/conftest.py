import json
import pytest
from pathlib import Path
from web_vitals_cli.parser import parse_lighthouse_json
from web_vitals_cli.types import LighthouseResult

@pytest.fixture
def sample_lh_json():
    return json.loads(Path("data/sample_lighthouse.json").read_text())

@pytest.fixture
def sample_result(sample_lh_json):
    return parse_lighthouse_json(sample_lh_json)