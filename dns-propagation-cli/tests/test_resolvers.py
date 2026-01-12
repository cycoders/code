from dns_propagation_cli.resolvers import RESOLVERS


def test_resolvers_valid():
    assert len(RESOLVERS) >= 15
    for r in RESOLVERS:
        assert "name" in r
        assert "ip" in r
        assert "location" in r
        assert r["name"]
        assert r["ip"]
