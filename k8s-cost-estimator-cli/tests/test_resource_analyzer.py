import pytest
from k8s_cost_estimator_cli.resource_analyzer import extract_resources, _cpu_to_cores, _mem_to_mib
from k8s_cost_estimator_cli.types import Resources


def test_cpu_parsing():
    assert _cpu_to_cores("500m") == 0.5
    assert _cpu_to_cores("2") == 2.0


def test_mem_parsing():
    assert _mem_to_mib("1Gi") == 1024.0
    assert _mem_to_mib("512Mi") == 512.0

@pytest.mark.parametrize("nodes", [1, 5])
def test_daemonset_extraction(sample_daemonset, nodes):
    res = extract_resources(sample_daemonset, nodes)
    assert res.cpu_cores == 0.1 * nodes
    assert res.mem_gib == 0.128 * nodes


def test_deployment_extraction(sample_deployment):
    res = extract_resources(sample_deployment)
    assert res.cpu_cores == 0.2 * 3  # 3 replicas
    assert res.mem_gib == 0.256 * 3
