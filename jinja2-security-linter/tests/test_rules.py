from jinja2 import Environment
from jinja2_security_linter.rules import check_unsafe_filter

def test_rule_visits_ast():
    env = Environment(autoescape=True)
    ast = env.parse("{{ x|safe }}")
    res = check_unsafe_filter(ast, "t.j2")
    assert len(res) == 1