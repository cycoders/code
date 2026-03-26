import whois
from typing import Dict, Any


def get_whois(domain: str, timeout: float) -> Dict[str, Any]:
    """Fetch WHOIS data."""
    try:
        w = whois.whois(domain)
        data = {
            "registrar": getattr(w, "registrar", None),
            "creation_date": str(getattr(w, "creation_date", None)),
            "expiration_date": str(getattr(w, "expiration_date", None)),
            "updated_date": str(getattr(w, "updated_date", None)),
            "name_servers": getattr(w, "name_servers", []),
            "registrant": str(getattr(w, "name", None)),
            "emails": [getattr(w, "email", None), getattr(w, "registrant_email", None)],
        }
        return {"whois": {k: v for k, v in data.items() if v is not None}}
    except Exception as e:
        return {"whois": {"error": str(e)}}