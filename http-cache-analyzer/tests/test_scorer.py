import pytest

from http_cache_analyzer.scorer import score_policy
from http_cache_analyzer.models import CachePolicy, CacheDirective


@pytest.mark.parametrize("url, policy_dict, expected_score_min, expected_sugg_contains", [
    ("https://ex.com/app.js", {"max_age": 31536000, "directives": [{"name": "immutable"}]}, 90, "Good"),
    ("https://ex.com/logo.png", {"max_age": 3600}, 40, "Long max-age"),
    ("https://ex.com/api/v1", {"directives": [{"name": "no-cache"}]}, 80, "Good"),
    ("https://ex.com/", {}, 0, "No cache"),
])
def test_score_policy(url, policy_dict, expected_score_min, expected_sugg_contains):
    policy = CachePolicy(**policy_dict)
    score, sugg = score_policy(policy, url)
    assert score >= expected_score_min
    assert expected_sugg_contains.lower() in sugg.lower()
