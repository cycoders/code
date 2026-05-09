import pytest
from csp_policy_builder.policy_generator import generate_csp, strictness_score
from csp_policy_builder.types import Resource


def test_generate_basic():
    res1 = Resource("https://ex/script.js", "https", "ex", "/script.js", "script-src")
    res2 = Resource("inline", "inline", None, "", "script-src", True, "'sha256-abc'", )
    policy = generate_csp([res1, res2])
    assert "script-src" in policy
    assert "ex" in policy
    assert "sha256-abc" in policy


def test_strictness():
    good = "default-src 'self'; script-src 'self'"
    assert strictness_score(good) > 80
    bad = "*; 'unsafe-inline' 'unsafe-eval'"
    assert strictness_score(bad) < 30
