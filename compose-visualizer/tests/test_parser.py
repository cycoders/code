import pytest
from pathlib import Path
from compose_visualizer.parser import parse_compose
from compose_visualizer.models import Compose


@pytest.fixture
def simple_compose() -> dict:
    return {
        "version": "3.8",
        "services": {
            "db": {"image": "postgres:15", "ports": ["5432:5432"]},
            "api": {"image": "python:3.12", "depends_on": ["db"]},
        },
    }


def test_parse_compose(tmp_path: Path, simple_compose: dict):
    file = tmp_path / "docker-compose.yml"
    import yaml
    file.write_text(yaml.dump(simple_compose))

    compose = parse_compose(file)
    assert isinstance(compose, Compose)
    assert len(compose.services) == 2
    assert compose.services["db"].name == "db"
    assert compose.services["api"].depends_on == ["db"]


def test_parse_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_compose(tmp_path / "missing.yml")