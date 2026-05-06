import collections
from typing import Dict, Any


class Evaluator:
    """Heuristic quality scorer for LLM responses."""

    HEDGES = ["i think", "probably", "maybe", "as far as i know", "i'm not sure", "it depends"]

    @staticmethod
    def evaluate(response: str, prompt_tokens: int, response_tokens: int) -> Dict[str, Any]:
        """Compute scores."""
        scores = {
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "efficiency": round(response_tokens / max(prompt_tokens, 1), 2),
        }

        # Repetition
        words = response.lower().split()
        if len(words) > 5:
            freq = collections.Counter(words)
            max_rep = max(freq.values())
            scores["repetition"] = round(max_rep / len(words), 2)

        # Confidence (hedge words)
        lower_resp = response.lower()
        hedge_count = sum(1 for hedge in Evaluator.HEDGES if hedge in lower_resp)
        scores["hedge_ratio"] = round(hedge_count / max(len(words) / 20, 1), 2)
        scores["confidence"] = max(0, 1 - scores["hedge_ratio"])

        return scores
