from typing import List

from .types import Resource


def classify_resources(resources: List[Resource]) -> List[Resource]:
    """Classify and expand resources to multiple directives if needed (e.g., script → connect-src)."""
    classified = []
    for res in resources:
        classified.append(res)
        if res.directive == "script-src":
            # Scripts often do fetches
            conn_res = Resource(
                url=res.url,
                scheme=res.scheme,
                host=res.host,
                path=res.path,
                directive="connect-src",
                is_inline=res.is_inline,
                hash_value=res.hash_value,
            )
            classified.append(conn_res)
    return classified
