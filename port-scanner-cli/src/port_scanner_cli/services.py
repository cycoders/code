import json
import re
from typing import Dict, Any

from importlib.resources import files

SERVICES_DB: Dict[str, Dict[str, Any]] = {}

try:
    services_text = files("port_scanner_cli.data").joinpath("services.json").read_text(encoding="utf-8")
    SERVICES_DB = json.loads(services_text)
except Exception:
    # Fallback minimal DB
    SERVICES_DB = {
        "22": {"name": "SSH", "patterns": ["openssh", "dropbear", "sshd"]},
        "80": {"name": "HTTP", "patterns": ["apache", "nginx", "lighttpd", "iis"]},
        "443": {"name": "HTTPS", "patterns": ["apache", "nginx"]},
        "3306": {"name": "MySQL", "patterns": ["mysql", "mariadb"]},
        "5432": {"name": "PostgreSQL", "patterns": ["postgresql"]},
    }


def get_services() -> Dict[str, Dict[str, Any]]:
    """Get services database."""
    return SERVICES_DB


def identify_service(port: int, banner: str) -> str:
    """Identify service from port and banner."""
    pstr = str(port)
    serv = get_services().get(pstr, {"name": "unknown", "patterns": []})
    name = serv["name"]
    banner_lower = banner.lower()
    for pattern in serv["patterns"]:
        if re.search(re.escape(pattern.lower()), banner_lower):
            return f"{name} ({pattern})"
    return name