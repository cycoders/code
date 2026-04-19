import json
import pytest
from pathlib import Path

from postman_auditor_cli.models import Collection


@pytest.fixture
def demo_collection():
    with open(Path(__file__).parent.parent / "examples" / "demo.json") as f:
        data = json.load(f)
    return Collection.model_validate(data)
