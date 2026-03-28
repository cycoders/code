from netmon_tui.models import Addr, Connection


def test_addr_namedtuple():
    a = Addr("1.2.3.4", 8080)
    assert a.ip == "1.2.3.4"
    assert a.port == 8080


def test_connection_str():
    c = Connection(
        local=Addr("127.0.0.1", 8080),
        raddr=Addr("127.0.0.1", None),
        status="LISTEN",
        pid=123,
        process_name="nginx",
    )
    assert "127.0.0.1:8080 → 127.0.0.1 [LISTEN]" in str(c)


def test_connection_frozen():
    c = Connection(Addr("1.1.1.1", 53), Addr("8.8.8.8", 12345), "ESTAB", 456, "dnsmasq")
    with pytest.raises(AttributeError):
        c.status = "CLOSED"  # frozen