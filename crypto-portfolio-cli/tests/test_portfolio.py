import pytest
from portfolio import calculate_portfolio

def test_calculate_portfolio():
    prices = {'btc': 60000.0, 'eth': 3000.0}
    holdings = {'btc': 0.5, 'eth': 2.0}
    result = calculate_portfolio(prices, holdings)
    assert result['holdings']['btc'] == 30000.0
    assert result['holdings']['eth'] == 6000.0
    assert result['total'] == 36000.0

def test_calculate_portfolio_missing_coin():
    prices = {'btc': 60000.0}
    holdings = {'btc': 0.5, 'eth': 2.0}
    result = calculate_portfolio(prices, holdings)
    assert result['holdings']['eth'] == 0.0
    assert result['total'] == 30000.0
