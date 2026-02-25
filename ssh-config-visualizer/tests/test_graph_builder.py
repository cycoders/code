import networkx as nx
from ssh_config_visualizer.graph_builder import build_ssh_graph
from ssh_config_visualizer.parser import parse_config_content


def test_build_simple_graph():
    content = """
Host foo
  HostName bar.com
  ProxyJump jump1
"""
    hosts = parse_config_content(content)
    G = build_ssh_graph(hosts)
    assert len(G.nodes) == 3
    assert "foo" in G
    assert "bar.com" in G
    assert "jump1" in G
    assert G.has_edge("foo", "bar.com")
    assert G.has_edge("foo", "jump1")


def test_proxycommand_parse():
    content = """
Host pc
  ProxyCommand ssh gateway nc %h 22
"""
    hosts = parse_config_content(content)
    G = build_ssh_graph(hosts)
    assert G.has_edge("pc", "gateway")


def test_multiple_proxyjump():
    content = """
Host multi
  ProxyJump a b,c
"""
    hosts = parse_config_content(content)
    G = build_ssh_graph(hosts)
    assert G.has_edge("multi", "a")
    assert G.has_edge("multi", "b")
    assert G.has_edge("multi", "c")