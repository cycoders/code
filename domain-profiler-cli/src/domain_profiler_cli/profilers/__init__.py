from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor


def profile_domain(
    domain: str,
    include_dns: bool = True,
    include_whois: bool = True,
    include_ssl: bool = True,
    include_headers: bool = True,
    include_tech: bool = True,
    include_security: bool = True,
    port: int = 443,
    use_http: bool = False,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """Run all profilers in parallel."""
    result: Dict[str, Any] = {"domain": domain}

    futures = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        if include_dns:
            futures.append(executor.submit(get_dns_records, domain, timeout))
        if include_whois:
            futures.append(executor.submit(get_whois, domain, timeout))
        if include_ssl:
            futures.append(executor.submit(get_ssl_info, domain, port, timeout))
        if include_headers or include_tech or include_security:
            futures.append(executor.submit(get_headers_and_html, domain, port, use_http, timeout))

        for future in as_completed(futures):
            section_data = future.result()
            if isinstance(section_data, dict) and len(section_data) == 1:
                result[list(section_data)[0]] = section_data[list(section_data)[0]]
            else:
                # headers_and_html
                headers, html = section_data
                result["headers"] = headers
                if include_tech:
                    result["tech"] = detect_tech(headers, html)
                if include_security:
                    ssl_key = "ssl"
                    result["security"] = get_security_score(headers, result.get("ssl", {}))

    return result

# Imports below to avoid circular

from .dns import get_dns_records
from .whois import get_whois
from .ssl import get_ssl_info
from .headers import get_headers_and_html
from .tech import detect_tech
from .security import get_security_score