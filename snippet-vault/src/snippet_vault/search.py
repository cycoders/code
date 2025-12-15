from typing import List
from rapidfuzz import fuzz

from .models import Snippet


def fuzzy_search(
    snippets: List[Snippet], query: str, threshold: int = 60, limit: int = None
) -> List[Snippet]:
    """Fuzzy search snippets by title, tags, content. Returns top matches sorted by score."""
    q_lower = query.lower()

    scored = []
    for snippet in snippets:
        title_score = fuzz.partial_ratio(q_lower, snippet.title.lower())
        tags_score = max(
            (fuzz.partial_ratio(q_lower, tag.lower()) for tag in snippet.tags), default=0
        )
        content_snip = snippet.content.lower()[:3000]
        content_score = fuzz.partial_ratio(q_lower, content_snip)
        max_score = max(title_score, tags_score, content_score)
        if max_score >= threshold:
            scored.append((max_score, snippet))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [snippet for _, snippet in scored[:limit]]
    return results
