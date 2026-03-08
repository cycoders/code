import pytest
from unittest.mock import Mock
from compose_visualizer.auditor import audit_compose
from compose_visualizer.models import Compose, Service


def test_audit_port_conflict():
    services = {
        "svc1": Mock(ports=["80:8080"], name="svc1"),
        "svc2": Mock(ports=["80:3000"], name="svc2"),
    }
    compose = Compose(services=services)
    issues = audit_compose(compose)
    assert any("Port 80 conflict" in issue for issue in issues)


def test_audit_no_image():
    services = {"svc": Mock(image=None, build=None, name="svc")}
    compose = Compose(services=services)
    issues = audit_compose(compose)
    assert "missing image or build" in issues[0]


def test_audit_clean():
    services = {
        "db": Mock(image="postgres", ports=["5432"], name="db"),
    }
    compose = Compose(services=services)
    issues = audit_compose(compose)
    assert len(issues) == 1  # healthcheck missing
