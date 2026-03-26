from src.domain_profiler_cli.profilers.security import get_security_score


def test_security_full_score():
    headers = {"strict-transport-security": "max-age=31536000"}
    ssl = {"not_after": "2030-01-01T00:00:00+00:00"}
    score_data = get_security_score(headers, ssl)
    assert score_data["score"] == 100


def test_security_low_score():
    headers = {}
    ssl = {"not_after": "2024-01-01T00:00:00+00:00"}  # expired
    score_data = get_security_score(headers, ssl)
    assert score_data["score"] < 50