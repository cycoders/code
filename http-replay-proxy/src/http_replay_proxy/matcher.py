from typing import Dict, Any, Optional, List

from .serialize import MATCH_HEADERS

def find_match(interactions: List[Dict[str, Any]], req_ser: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find first matching interaction by request."""
    for inter in interactions:
        if requests_match(req_ser, inter['request']):
            return inter
    return None

def requests_match(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Match requests: method/path/query + key headers."""
    if a['method'] != b['method']:
        return False
    if a['path'] != b['path']:
        return False
    if a['query'] != b['query']:
        return False
    for header in MATCH_HEADERS:
        if a['headers'].get(header) != b['headers'].get(header):
            return False
    return True