from typing import List

import networkx as nx

from ssh_config_visualizer.parser import SSHHost


def validate_config(hosts: List[SSHHost], graph: nx.DiGraph) -> List[str]:
    """Validate config: cycles, duplicates, basic conflicts."""
    issues: List[str] = []

    # Duplicate patterns
    patterns = [h.pattern for h in hosts]
    dups = {p: count for p, count in zip(patterns, [patterns.count(p) for p in patterns]) if count > 1}
    if dups:
        issues.append(f"Duplicate Host patterns: {list(dups.keys())}")

    # Cycles in proxy chains
    try:
        _ = nx.find_cycle(graph, orientation="original")
        issues.append("ProxyJump cycles detected (risk of SSH loops)")
    except nx.NetworkXNoCycle:
        pass

    # Orphaned proxies (no incoming/outgoing)
    proxies = {n for n, d in graph.nodes(data=True) if d["type"].startswith("proxy")}
    hosts_set = {h.pattern for h in hosts}
    orphans = proxies - set(graph.nodes) & hosts_set  # rough
    if orphans:
        issues.append(f"Orphan proxy hosts: {list(orphans)[:5]}")

    # Conflicting HostName in same pattern (rare)
    for host in hosts:
        if len(host.config.get("hostname", [])) > 1:
            issues.append(f"Multiple HostName for {host.pattern}")

    return issues