import pytest
from traceroute_visualizer.parser import parse_traceroute_output
from traceroute_visualizer.models import Hop
INF = float('inf')

@pytest.fixture
def standard_trace():
    return """
1  192.168.1.1  1.2 ms  1.1 ms  1.3 ms
2  10.0.0.1  *  *  5.0 ms
3  8.8.8.8  10.0 ms !H  9.5 ms  10.2 ms
"""

def test_parse_standard(standard_trace):
    hops = parse_traceroute_output(standard_trace)
    assert len(hops) == 3
    assert hops[0].hop_num == 1
    assert hops[0].ip == "192.168.1.1"
    assert hops[0].rtts == pytest.approx([1.2, 1.1, 1.3])
    assert hops[1].rtts == [INF, INF, 5.0]
    assert hops[2].rtts == pytest.approx([10.0, 9.5, 10.2])

def test_parse_timeout_only():
    text = "1  1.1.1.1  * * *"
    hops = parse_traceroute_output(text)
    assert len(hops) == 1
    assert hops[0].rtts == [INF, INF, INF]

def test_parse_single_probe():
    text = "1  1.1.1.1  5.0 ms"
    hops = parse_traceroute_output(text)
    assert hops[0].rtts == [5.0, INF, INF]

def test_empty():
    assert parse_traceroute_output("") == []

def test_malformed():
    text = "invalid line\n1 abc"
    hops = parse_traceroute_output(text)
    assert len(hops) == 0