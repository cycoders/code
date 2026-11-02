import ast
from middleware_order_linter.analyzer import analyze

def test_no_violations_on_clean_app():
    assert analyze("tests/fixtures/clean_app.py", "flask", None) == []