from typing import Dict, List, Tuple, Any

import k8s_netpol_sim.models as m


def labels_match(pod_ns_labels: Dict[str, str], selector: m.LabelSelector | None) -> bool:
    """Check if labels match selector (all match_labels must match)."""
    if selector is None or selector.match_labels is None:
        return True
    return all(pod_ns_labels.get(k) == v for k, v in selector.match_labels.items())


def rule_matches(
    rule: m.Rule,
    remote_pod_labels: Dict[str, str],
    remote_ns_labels: Dict[str, str],
    port: int,
    protocol: str = "TCP",
) -> bool:
    """Check if rule allows to/from remote (port + any peer match)."""
    if rule.ports is not None and port not in rule.ports:
        return False
    for peer in rule.peers:
        pod_match = labels_match(remote_pod_labels, peer.pod_selector)
        ns_match = labels_match(remote_ns_labels, peer.namespace_selector)
        if pod_match and ns_match:
            return True
    return False


def check_direction(
    policies: List[m.NetPol],
    pod_ns: str,
    pod_labels: Dict[str, str],
    pod_ns_labels: Dict[str, str],
    direction: str,
    remote_ns_labels: Dict[str, str],
    remote_pod_labels: Dict[str, str],
    port: int,
    protocol: str,
) -> Tuple[bool, Dict[str, List[str]]]:
    """Check if direction allowed by all relevant policies."""
    relevant_policies = [
        p
        for p in policies
        if (
            p.namespace == pod_ns
            and labels_match(pod_labels, p.pod_selector)
            and (p.policy_types is None or direction.upper() in p.policy_types)
        )
    ]
    if not relevant_policies:
        return True, {"allowing": [], "blocking": []}

    details = {"allowing": [], "blocking": []}
    rules_key = "ingress" if direction == "ingress" else "egress"
    for pol in relevant_policies:
        rules: List[m.Rule] | None = getattr(pol, rules_key, None)
        pol_name = pol.name or f"{pod_ns}/{direction}"
        if rules is None or not any(
            rule_matches(rule, remote_pod_labels, remote_ns_labels, port, protocol)
            for rule in rules
        ):
            details["blocking"].append(pol_name)
        else:
            details["allowing"].append(pol_name)
    allowed = len(details["blocking"]) == 0
    return allowed, details


def simulate(
    topology: m.Topology,
    policies: List[m.NetPol],
    src_ns: str,
    src_pod: str,
    dst_ns: str,
    dst_pod: str,
    port: int,
    protocol: str = "TCP",
) -> Tuple[bool, Dict[str, Any]]:
    """Simulate full traffic flow."""
    if src_ns not in topology.namespaces:
        raise ValueError(f"Unknown namespace: {src_ns}")
    src_ns_topo = topology.namespaces[src_ns]
    if src_pod not in src_ns_topo.pods:
        raise ValueError(f"Unknown pod: {src_ns}/{src_pod}")
    src_pod_labels = src_ns_topo.pods[src_pod].labels
    src_ns_labels = src_ns_topo.labels

    if dst_ns not in topology.namespaces:
        raise ValueError(f"Unknown namespace: {dst_ns}")
    dst_ns_topo = topology.namespaces[dst_ns]
    if dst_pod not in dst_ns_topo.pods:
        raise ValueError(f"Unknown pod: {dst_ns}/{dst_pod}")
    dst_pod_labels = dst_ns_topo.pods[dst_pod].labels
    dst_ns_labels = dst_ns_topo.labels

    # Egress check (src perspective)
    egress_ok, egress_details = check_direction(
        policies,
        src_ns,
        src_pod_labels,
        src_ns_labels,
        "egress",
        dst_ns_labels,
        dst_pod_labels,
        port,
        protocol,
    )
    # Ingress check (dst perspective)
    ingress_ok, ingress_details = check_direction(
        policies,
        dst_ns,
        dst_pod_labels,
        dst_ns_labels,
        "ingress",
        src_ns_labels,
        src_pod_labels,
        port,
        protocol,
    )

    allowed = egress_ok and ingress_ok
    return (
        allowed,
        {
            "egress": egress_details,
            "ingress": ingress_details,
            "src": f"{src_ns}/{src_pod}",
            "dst": f"{dst_ns}/{dst_pod}",
            "port_protocol": f"{port}/{protocol}",
        },
    )