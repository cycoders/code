import requests
from typing import Dict, List

def get_prices(coin_ids: List[str], vs_currency: str = 'usd') -> Dict[str, float]:
    """Fetch prices from CoinGecko API."""
    if not coin_ids:
        raise ValueError('No coin IDs provided')
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': ','.join(coin_ids),
        'vs_currencies': vs_currency.lower()
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    prices = {}
    for coin in coin_ids:
        price = data.get(coin, {}).get(vs_currency.lower(), 0.0)
        prices[coin] = float(price)
    return prices
