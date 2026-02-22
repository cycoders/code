import pytest
from env_expander_cli.expander import EnvExpander
from env_expander_cli.expander_errors import UndefinedVariable, CycleDetected


@pytest.fixture
def simple_env():
    return {"A": "hello", "B": "${A} world"}


def test_expand_simple(simple_env):
    expander = EnvExpander(simple_env)
    expanded = expander.expand_all()
    assert expanded["B"] == "hello world"


def test_nested():
    env = {"C": "foo", "B": "${C}", "A": "pre-${B}-post"}
    expander = EnvExpander(env)
    expanded = expander.expand_all()
    assert expanded["A"] == "pre-foo-post"


def test_default_missing():
    env = {"A": "${B:-fallback}"}
    expander = EnvExpander(env)
    expanded = expander.expand_all()
    assert expanded["A"] == "fallback"


def test_default_nested():
    env = {"A": "${B:-${C:-deep}}", "C": "shallow"}
    expander = EnvExpander(env)
    expanded = expander.expand_all()
    assert expanded["A"] == "shallow"


def test_cycle():
    env = {"A": "${A}"}
    expander = EnvExpander(env)
    with pytest.raises(CycleDetected, match="A"):
        expander.expand_all()


def test_undefined():
    env = {"A": "${B}"}
    expander = EnvExpander(env)
    with pytest.raises(UndefinedVariable, match="B"):
        expander.expand_all()


def test_empty_with_colon_default():
    env = {"A": "", "B": "${A:-fallback}"}
    expander = EnvExpander(env)
    expanded = expander.expand_all()
    assert expanded["B"] == "fallback"