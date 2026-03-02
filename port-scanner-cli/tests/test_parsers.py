import pytest
from port_scanner_cli.scanner import parse_ports, parse_targets


def test_parse_ports_presets():
    assert parse_ports("top100") == [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723,
        3306, 3389, 5432, 5900, 8080, 8443, 27017, 3000, 5000, 5433, 5901,
        6379, 8081, 9200, 11211, 27017
    ]
    assert parse_ports("WeB") == [80, 443, 8080, 8443, 3000, 5000, 8000]


def test_parse_ports_custom():
    assert parse_ports("80,443") == [80, 443]
    assert parse_ports("1-5,3-4") == [1, 2, 3, 4, 5]
    assert parse_ports("80, 80") == [80]


def test_parse_ports_invalid():
    with pytest.raises(ValueError, match="Invalid port"):
        parse_ports("abc")
    with pytest.raises(ValueError, match="out of range"):
        parse_ports("70000")


def test_parse_targets_single():
    assert parse_targets("127.0.0.1") == ["127.0.0.1"]
    assert parse_targets("localhost,example.com") == ["localhost", "example.com"]


def test_parse_targets_cidr():
    ips = parse_targets("192.168.1.0/24")
    assert len(ips) == 254
    assert ips[0] == "192.168.1.1"
    assert ips[-1] == "192.168.1.254"


def test_parse_targets_invalid():
    with pytest.raises(ValueError, match="Invalid CIDR"):
        parse_targets("999.999.999.999/24")
