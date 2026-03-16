import re
from typing import List


def suggest(query: str) -> List[str]:
    """Basic rule-based suggestions."""
    lower_q = query.lower().strip()
    suggestions = []
    if "select" in lower_q and "where" not in lower_q[:lower_q.find("select") + 6]:
        suggestions.append("❌ Missing WHERE clause - full table scan?")
    if "select " in lower_q and "limit" not in lower_q:
        suggestions.append("➕ Add LIMIT for paginated queries")
    if re.search(r"like\s*\?", lower_q) or "%" in lower_q:
        suggestions.append("🔍 Consider trigram/full-text index for LIKE '%...?'")
    if "join" in lower_q and "index" not in lower_q:
        suggestions.append("📈 Check JOIN indexes and order")
    if len(lower_q) > 500:
        suggestions.append("📏 Simplify/complex subquery - rewrite or CTE?")
    return suggestions
