import pytest

from k8s_netpol_sim.models import Topology, NetPol, LabelSelector, Pod, NamespaceTopology


@pytest.fixture
def sample_topology():
    return Topology.model_validate(
        {
            "namespaces": {
                "default": {
                    "labels": {"team": "backend"},
                    "pods": {
                        "web": {"name": "web", "labels": {"app": "web"}},
                    },
                },
                "frontend": {
                    "labels": {},
                    "pods": {
                        "app": {"name": "app", "labels": {"app": "frontend"}},
                    },
                },
            }
        }
    )


@pytest.fixture
def sample_policy():
    return NetPol.model_validate(
        {
            "namespace": "default",
            "name": "test-pol",
            "pod_selector": {"match_labels": {"app": "web"}},
            "ingress": [
                {
                    "peers": [{"pod_selector": {"match_labels": {"app": "frontend"}}}],
                    "ports": [80],
                }
            ],
        }
    )


def test_model_parsing(sample_topology, sample_policy):
    assert sample_topology.namespaces["default"].pods["web"].labels["app"] == "web"
    assert sample_policy.namespace == "default"
    assert sample_policy.pod_selector.match_labels["app"] == "web"