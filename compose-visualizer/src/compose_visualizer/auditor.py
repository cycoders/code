from typing import List

import re

from .models import Compose


Issue = str


def audit_compose(compose: Compose) -> List[Issue]:
    """Run comprehensive audits."""

    issues: List[Issue] = []

    services = compose.services

    # 1. Dependency cycles
    from .graph import find_cycles, build_graph  # local import ok
    cycles = find_cycles(build_graph(services))
    for cycle in cycles:
        issues.append(f"Dependency cycle: {' -> '.join(cycle)} -> {cycle[0]}")

    # 2. Port conflicts
    port_usage: Dict[int, List[str]] = {}
    for svc in services.values():
        for port_str in svc.ports:
            match = re.match(r"^(\d+)(:\d+)?(/\w+)?$", port_str)
            if match:
                host_port = int(match.group(1))
                if host_port in port_usage:
                    port_usage[host_port].append(svc.name)
                else:
                    port_usage[host_port] = [svc.name]
    for port, svcs in port_usage.items():
        if len(svcs) > 1:
            issues.append(f"Port {port} conflict: {', '.join(svcs)}")

    # 3. Services without image or build
    for name, svc in services.items():
        if not svc.image and not svc.build:
            issues.append(f"Service '{name}' missing image or build")

    # 4. No healthcheck
    for name, svc in services.items():
        if not svc.healthcheck:
            issues.append(f"Service '{name}' missing healthcheck")

    # 5. Unused networks
    used_nets = set()
    for svc in services.values():
        used_nets.update(svc.networks)
    for net in compose.networks:
        if net not in used_nets:
            issues.append(f"Unused network: {net}")

    # 6. Orphan services (no incoming/outgoing deps)
    graph = build_graph(services)
    incoming = {s: 0 for s in services}
    for deps in graph.values():
        for d in deps:
            incoming[d] = incoming.get(d, 0) + 1
    for name, indeg in incoming.items():
        if indeg == 0 and not graph.get(name):
            issues.append(f"Orphan service: {name} (no deps)")

    return issues