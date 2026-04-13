import pytest
from k8s_netpol_sim.simulator import labels_match, rule_matches, check_direction, simulate
from k8s_netpol_sim.models import (
    LabelSelector,
    Peer,
    Rule,
    NetPol,
    Pod,
    NamespaceTopology,
    Topology,
)


def test_labels_match():
    assert labels_match({"app": "web"}, LabelSelector(match_labels={"app": "web"}))
    assert not labels_match({"app": "api"}, LabelSelector(match_labels={"app": "web"}))
    assert labels_match({"app": "web"}, None)
    assert labels_match({}, LabelSelector(match_labels={}))  # empty selector matches


def test_rule_matches():
    rule = Rule(
        peers=[Peer(pod_selector=LabelSelector(match_labels={"app": "frontend"}))],
        ports=[80],
    )
    assert rule_matches(rule, {"app": "frontend"}, {"team": "fe"}, 80)
    assert not rule_matches(rule, {"app": "backend"}, {}, 8080)
    assert rule_matches(
        Rule(peers=[Peer()], ports=None), {"app": "any"}, {}, 443
    )  # any peer, any port


@pytest.mark.parametrize(
    "direction, has_restricting_pol, rules_match, expected",
    [
        ("egress", False, False, (True, {"allowing": [], "blocking": []})),
        ("ingress", True, True, (True, {"allowing": ["pol1"], "blocking": []})),
        ("egress", True, False, (False, {"allowing": [], "blocking": ["pol1"]})),
    ],
)
def test_check_direction(direction, has_restricting_pol, rules_match, expected):
    policies = []
    if has_restricting_pol:
        rules = [Rule(peers=[Peer()])] if rules_match else []
        policies = [
            NetPol(
                namespace="default",
                pod_selector=LabelSelector(),
                policy_types=[direction.upper()],
                **({direction: rules}),
            )
        ]
    ok, details = check_direction(
        policies,
        "default",
        {"app": "web"},
        {"ns": "default"},
        direction,
        {"remote": "ns"},
        {"remote": "pod"},
        80,
    )
    assert ok == expected[0]
    assert details == expected[1]


def test_simulate_full():
    topo = Topology(
        namespaces={
            "default": NamespaceTopology(
                labels={}, pods={"web": Pod(name="web", labels={"app": "web"})}
            ),
            "fe": NamespaceTopology(pods={"app": Pod(name="app", labels={"app": "fe"})}),
        }
    )
    pols = [
        NetPol(
            namespace="default",
            name="allow-fe",
            pod_selector=LabelSelector(match_labels={"app": "web"}),
            policy_types=["Ingress"],
            ingress=[
                Rule(
                    peers=[Peer(pod_selector=LabelSelector(match_labels={"app": "fe"}))],
                    ports=[80],
                )
            ],
        )
    ]
    allowed, _ = simulate(topo, pols, "fe", "app", "default", "web", 80)
    assert allowed

    # Block by changing label
    pols[0].ingress[0].peers[0].pod_selector.match_labels["app"] = "wrong"
    allowed, details = simulate(topo, pols, "fe", "app", "default", "web", 80)
    assert not allowed
    assert "allow-fe" in details["ingress"]["blocking"]


def test_errors():
    topo = Topology(namespaces={})
    pols = []
    with pytest.raises(ValueError, match="Unknown namespace"):
        simulate(topo, pols, "missing", "pod", "default", "pod", 80)