import pytest
from unittest.mock import Mock, patch
import requests
from api import get_prices

def test_get_prices_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'bitcoin': {'usd': 60000.5},
        'ethereum': {'usd': 3000.25}
    }
    with patch('requests.get', return_value=mock_response):
        prices = get_prices(['bitcoin', 'ethereum'])
        assert prices['bitcoin'] == 60000.5
        assert prices['ethereum'] == 3000.25

def test_get_prices_missing_coin():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'bitcoin': {'usd': 60000.0}}
    with patch('requests.get', return_value=mock_response):
        prices = get_prices(['bitcoin', 'unknown'])
        assert prices['unknown'] == 0.0

def test_get_prices_http_error():
    mock_response = Mock()
    mock_response.status_code = 429
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            get_prices(['btc'])
