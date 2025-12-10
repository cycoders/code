from typing import Dict

def calculate_portfolio(prices: Dict[str, float], holdings: Dict[str, float]) -> Dict[str, float]:
    """Calculate portfolio values."""
    holdings_values: Dict[str, float] = {}
    total = 0.0
    for coin, amount in holdings.items():
        value = amount * prices.get(coin, 0.0)
        holdings_values[coin] = value
        total += value
    return {'holdings': holdings_values, 'total': total}
