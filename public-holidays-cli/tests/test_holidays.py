import pytest
from unittest.mock import patch, MagicMock

import requests
from holidays import get_available_countries, get_holidays, get_country_code


@patch("requests.get")
def test_get_available_countries(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"countryCode": "US", "name": "United States"},
        {"countryCode": "GB", "name": "United Kingdom"},
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_available_countries()

    assert len(result) == 2
    assert result[0]["countryCode"] == "US"
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_holidays(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"date": "2024-01-01", "localName": "New Year's Day", "name": "New Year's Day", "fixed": True, "global": False}
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_holidays(2024, "US")

    assert len(result) == 1
    assert result[0]["date"] == "2024-01-01"
    mock_get.assert_called_once_with("https://date.nager.at/Api/v3/PublicHolidays/2024/US")


@patch("holidays.get_available_countries")
def test_get_country_code_valid(mock_countries: MagicMock) -> None:
    mock_countries.return_value = [
        {"countryCode": "US", "name": "United States"},
        {"countryCode": "GB", "name": "United Kingdom"},
    ]

    assert get_country_code("US") == "US"
    assert get_country_code("United States") == "US"
    assert get_country_code("gb") == "GB"

    mock_countries.assert_called_once()


@patch("holidays.get_available_countries")
def test_get_country_code_invalid(mock_countries: MagicMock) -> None:
    mock_countries.return_value = [{"countryCode": "US", "name": "United States"}]

    with pytest.raises(ValueError, match="Country 'ZZ' not found"):
        get_country_code("ZZ")

    mock_countries.assert_called_once()