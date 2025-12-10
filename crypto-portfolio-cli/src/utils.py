from typing import Dict

def parse_holdings(holdings_str: str) -> Dict[str, float]:
    """Parse 'coin:amount,coin:amount' string."""
    holdings = {}
    pairs = [p.strip() for p in holdings_str.split(',')]
    for pair in pairs:
        if ':' not in pair:
            raise ValueError(f'Invalid pair format: {pair}')
        coin, amt_str = pair.split(':', 1)
        coin = coin.strip().lower()
        try:
            amount = float(amt_str.strip())
        except ValueError:
            raise ValueError(f'Invalid amount in {pair}: {amt_str}')
        holdings[coin] = amount
    if not holdings:
        raise ValueError('No valid holdings provided')
    return holdings
