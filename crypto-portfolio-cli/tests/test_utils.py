import pytest
from utils import parse_holdings

def test_parse_holdings():
    result = parse_holdings('bitcoin:0.1,ethereum:2.5,solana:100')
    expected = {'bitcoin': 0.1, 'ethereum': 2.5, 'solana': 100.0}
    assert result == expected

def test_parse_holdings_invalid_amount():
    with pytest.raises(ValueError, match='Invalid amount'):
        parse_holdings('btc:abc')

def test_parse_holdings_empty():
    with pytest.raises(ValueError, match='No valid holdings'):
        parse_holdings('')
