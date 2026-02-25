import io
from ssh_config_visualizer.parser import parse_config_content, SSHHost


def test_parse_simple():
    content = """
Host foo
  HostName bar.com
"""
    hosts = parse_config_content(content)
    assert len(hosts) == 1
    assert hosts[0].pattern == "foo"
    assert hosts[0].config["hostname"] == ["bar.com"]


def test_parse_proxyjump():
    content = """
Host baz
  ProxyJump host1, host2 host3
"""
    hosts = parse_config_content(content)
    assert hosts[0].config["proxyjump"] == ["host1, host2 host3"]


def test_parse_multiline_option():
    content = """
Host multiline
  ProxyCommand \
    ssh jump nc %h 22
"""
    hosts = parse_config_content(content)
    assert "proxycommand" in hosts[0].config
    assert "ssh jump nc" in hosts[0].config["proxycommand"][0]