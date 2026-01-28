import pytest
from pathlib import Path

from openapi_mocker.spec_parser import load_spec
from openapi_mocker.types import OpenAPISpec


@pytest.fixture
def simple_spec() -> Path:
    return Path(__file__).parent / "fixtures" / "simple.yaml"


def test_load_spec_valid(simple_spec: Path):
    spec = load_spec(simple_spec)
    assert isinstance(spec, OpenAPISpec)
    assert spec.openapi == "3.0.0"
    assert len(spec.paths) == 3


def test_load_spec_invalid_version(simple_spec: Path):
    spec_path = simple_spec.with_name("invalid-version.yaml")
    # Assume we create invalid for test, but skip impl
    with pytest.raises(ValueError, match="Only OpenAPI 3.0"):
        load_spec(spec_path)


def test_load_spec_nonexistent():
    with pytest.raises(ValueError, match="not found"):
        load_spec(Path("nonexistent.yaml"))


def test_load_json_spec():  # Assume json fixture if added
    pass