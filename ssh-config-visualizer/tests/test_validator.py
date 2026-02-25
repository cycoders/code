import networkx as nx
from ssh_config_visualizer.validator import validate_config
from ssh_config_visualizer.parser import parse_config_content, SSHHost
from ssh_config_visualizer.graph_builder import build_ssh_graph


def test_no_issues():
    content = """
Host good
  HostName ok.com
"""
    hosts = parse_config_content(content)
    G = build_ssh_graph(hosts)
    issues = validate_config(hosts, G)
    assert len(issues) == 0


def test_cycle_detection():
    content = """
Host a
  ProxyJump b
a b
  ProxyJump a
""".replace("a b", "Host b")
    hosts = parse_config_content(content)
    G = build_ssh_graph(hosts)
    issues = validate_config(hosts, G)
    assert any("cycle" in i for i in issues)


def test_duplicate_patterns():
    hosts = [SSHHost("dup", {}), SSHHost("dup", {})]
    G = nx.DiGraph()
    issues = validate_config(hosts, G)
    assert "Duplicate" in issues[0]