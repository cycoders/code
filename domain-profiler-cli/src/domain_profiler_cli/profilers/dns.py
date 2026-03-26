import dns.resolver
import dns.exception
from typing import Dict, Any


def get_dns_records(domain: str, timeout: float) -> Dict[str, Any]:
    """Fetch common DNS records."""
    records: Dict[str, list] = {}
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    for qtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
        try:
            answers = resolver.resolve(domain, qtype)
            records[qtype] = [r.to_text().rstrip(".") for r in answers]
        except (dns.exception.DNSException, Exception):
            pass

    return {"dns": records if records else {"error": "No records found"}}