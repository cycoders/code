import pytest
from csp_policy_builder.resource_classifier import classify_resources
from csp_policy_builder.types import Resource


def test_classify_expands_connect():
    res = Resource(url="https://ex/script.js", scheme="https", host="ex", path="/script.js", directive="script-src")
    classified = classify_resources([res])
    assert len(classified) == 2
    assert any(r.directive == "connect-src" for r in classified)
