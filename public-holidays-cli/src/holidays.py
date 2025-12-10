import requests
from typing import List, Dict, Any

BASE_URL = "https://date.nager.at/Api/v3"


def get_available_countries() -> List[Dict[str, str]]:
    response = requests.get(f"{BASE_URL}/AvailableCountries")
    response.raise_for_status()
    return response.json()


def get_holidays(year: int, country_code: str) -> List[Dict[str, Any]]:
    response = requests.get(f"{BASE_URL}/PublicHolidays/{year}/{country_code}")
    response.raise_for_status()
    return response.json()


def get_country_code(name_or_code: str) -> str:
    countries = get_available_countries()
    for country in countries:
        if (
            country["countryCode"].lower() == name_or_code.lower()
            or country["name"].lower() == name_or_code.lower()
        ):
            return country["countryCode"]
    raise ValueError(f"Country '{name_or_code}' not found. Use 'countries' command to list available countries.")