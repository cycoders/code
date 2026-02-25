import re
from typing import List

import networkx as nx

from ssh_config_visualizer.parser import SSHHost


def build_ssh_graph(hosts: List[SSHHost]) -> nx.DiGraph:
    """Build directed graph from SSH hosts (nodes: hosts/names/proxies, edges: relations)."""
    G = nx.DiGraph()

    for host in hosts:
        pattern = host.pattern
        G.add_node(pattern, type="host_pattern", config=host.config)

        # HostName
        hostname = host.config.get("hostname")
        if hostname:
            hn = hostname[0]
            G.add_node(hn, type="hostname")
            G.add_edge(pattern, hn, relation="hostname")

        # ProxyJump (comma/space split)
        proxy_jumps = host.config.get("proxyjump", [])
        for pj_raw in proxy_jumps:
            pjs = [pj.strip() for pj in re.split(r"[,\s]+", pj_raw)]
            for pj in pjs:
                if pj:
                    G.add_node(pj, type="proxyjump")
                    G.add_edge(pattern, pj, relation="proxyjump")

        # ProxyCommand (simple ssh host parse)
        proxy_cmds = host.config.get("proxycommand", [])
        for cmd in proxy_cmds:
            match = re.search(r"ssh\s+[^\s]+\s+([^\s]+)", cmd)
            if match:
                pj_host = match.group(1)
                G.add_node(pj_host, type="proxycommand")
                G.add_edge(pattern, pj_host, relation="proxycommand")

    return G