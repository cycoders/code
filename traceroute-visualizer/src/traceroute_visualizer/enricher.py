import subprocess
from typing import Optional, Tuple
from .models import Hop


def enrich_hop(hop: Hop) -> None:
    """
    Enrich hop IP with ASN/org/country via whois.cymru.com.
    """
    asn, org, country = _query_cymru_whois(hop.ip)
    hop.asn = asn
    hop.org = org
    hop.country = country


def _query_cymru_whois(ip: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        out = subprocess.check_output(
            ['whois', '-h', 'whois.cymru.com', ip],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10
        ).strip()
        if out:
            parts = out.split('|')
            if len(parts) >= 4:
                return (
                    parts[0].strip(),
                    parts[1].strip(),
                    parts[2].strip()
                )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    return None, None, None