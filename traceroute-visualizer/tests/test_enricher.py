import pytest
from unittest.mock import patch, MagicMock
from traceroute_visualizer.enricher import enrich_hop
from traceroute_visualizer.models import Hop

@patch('subprocess.check_output')
def test_enrich_success(mock_check_output):
    mock_output = MagicMock()
    mock_output.decode.return_value = "15169 | GOOGLE | US | 8.8.8.8\n"
    mock_check_output.return_value = mock_output
    hop = Hop(hop_num=1, ip="8.8.8.8", rtts=[10.0, 10.0, 10.0])
    enrich_hop(hop)
    assert hop.asn == "15169"
    assert hop.org == "GOOGLE"
    assert hop.country == "US"

@patch('subprocess.check_output')
def test_enrich_fail(mock_check_output):
    mock_check_output.side_effect = Exception("whois fail")
    hop = Hop(hop_num=1, ip="invalid", rtts=[1.0])
    enrich_hop(hop)
    assert hop.asn is None
    assert hop.org is None
    assert hop.country is None