import re
from typing import Dict

PATTERNS: Dict[str, str] = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone_us": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "phone_intl": r"\+?\d[\d\s\-\(\)]{7,}",
    "ipv4": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    "ipv6": r"([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}",
    "ssn_us": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d{4}[\-\s]?){4}\b",
    "zip_us": r"\b\d{5}(?:-\d{4})?\b",
    "street_address": r"\b\d+\s+[A-Za-z\s]+(?:St|Rd|Ave|Blvd|Dr|Ln|Ct)\.?,?\s*[A-Za-z\s]*,?\s*"
}

PII_TYPE_FAKER_MAP = {
    "email": "email",
    "phone_us": "phone_number",
    "phone_intl": "phone_number",
    "ssn_us": "ssn",
    "credit_card": "credit_card_number",
    "zip_us": "postcode",
    "street_address": "street_address",
    "ipv4": "ipv4",
    "ipv6": "ipv6_private",
}

COMPILED_PATTERNS = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in PATTERNS.items()}
