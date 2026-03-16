import re
import hashlib
from typing import Dict


def fingerprint(query: str) -> str:
    """Normalize query and return short hash for grouping."""
    # Remove comments
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL | re.MULTILINE)
    # Lowercase
    query = query.lower()
    # Remove string literals
    query = re.sub(r"'([^']|\\.)*'", "'?'", query)
    # Remove numbers and hex
    query = re.sub(r"\b(?:(?:0x)?[0-9a-f]+|\d+(?:\.\d+)?)\b", "?", query)
    # Normalize whitespace
    query = re.sub(r"\s+", " ", query)
    query = query.strip()
    # Remove empty params
    query = re.sub(r"\s*\?\s*", " ? ", query)
    # Hash
    return hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]


def fingerprint_sample_queries(queries: Dict[str, str]) -> Dict[str, str]:
    """Map fp to sample query."""
    return {fp: query[:200] + "..." for fp, query in queries.items()}
