'''Unit tests for client.py. Covers happy path, errors, edge cases.''' 

import pytest
from unittest.mock import MagicMock

from k8s_explorer_tui.client import K8sExplorerClient


@pytest.fixture
def mock_k8s(mocker):
    """Mock Kubernetes APIs."""
    mocker.patch("kubernetes.config.load_kube_config")
    core_mock = MagicMock()
    apps_mock = MagicMock()
    mocker.patch("kubernetes.client.CoreV1Api", return_value=core_mock)
    mocker.patch("kubernetes.client.AppsV1Api", return_value=apps_mock)
    return core_mock, apps_mock


def test_get_namespaces(mock_k8s):
    """List namespaces."""
    core, _ = mock_k8s
    mock_ns = MagicMock(metadata=MagicMock(name="default"))
    mock_ns2 = MagicMock(metadata=MagicMock(name="kube-system"))
    core.list_namespace.return_value.items = [mock_ns, mock_ns2]

    client = K8sExplorerClient()
    assert client.get_namespaces() == ["default", "kube-system"]


def test_get_deployments_info(mock_k8s):
    """Deployments with replicas."""
    _, apps = mock_k8s
    mock_dep = MagicMock()
    mock_dep.metadata.name = "nginx"
    mock_dep.status.ready_replicas = 3
    mock_dep.spec.replicas = 3
    apps.list_namespaced_deployment.return_value.items = [mock_dep]

    client = K8sExplorerClient()
    deps = client.get_deployments_info("default")
    assert len(deps) == 1
    assert deps[0]["name"] == "nginx"
    assert deps[0]["ready"] == 3
    assert deps[0]["desired"] == 3


def test_get_pods_info(mock_k8s):
    """Pods with status/restarts."""
    core, _ = mock_k8s
    mock_pod = MagicMock()
    mock_pod.metadata.name = "pod-1"
    mock_pod.status.phase = "Running"
    cont_status = MagicMock(restart_count=2)
    mock_pod.status.container_statuses = [cont_status]
    core.list_namespaced_pod.return_value.items = [mock_pod]

    client = K8sExplorerClient()
    pods = client.get_pods_info("default")
    assert len(pods) == 1
    assert pods[0]["name"] == "pod-1"
    assert pods[0]["status"] == "Running"
    assert pods[0]["restarts"] == 2


def test_get_pod_logs(mock_k8s):
    """Fetch pod logs."""
    core, _ = mock_k8s
    core.read_namespaced_pod_log.return_value = "test log\nline 2"

    client = K8sExplorerClient()
    logs = client.get_pod_logs("ns", "pod", tail_lines=10)
    assert "test log" in logs


def test_client_error_graceful(mock_k8s, mocker):
    """API errors handled."""
    core, _ = mock_k8s
    core.list_namespaced_pod.side_effect = Exception("API fail")

    client = K8sExplorerClient()
    pods = client.get_pods_info("default")
    assert pods == []  # Returns empty, no crash