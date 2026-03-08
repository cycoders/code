import pytest
from compose_visualizer.models import Service, Compose


def test_service_model():
    data = {
        "image": "postgres:15",
        "ports": ["5432:5432"],
        "depends_on": ["redis"],
    }
    svc = Service.model_validate(data)
    assert svc.image == "postgres:15"
    assert svc.ports == ["5432:5432"]
    assert svc.depends_on == ["redis"]


def test_compose_model():
    compose = Compose(services={}, version="3.8")
    assert compose.version == "3.8"
    assert len(compose.services) == 0