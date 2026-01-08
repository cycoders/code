import pytest
from py_api_diff.differ import diff
from py_api_diff.models import ApiElement, ArgSig


@pytest.fixture
def sample_old():
    return {
        ApiElement("mod.func", "function", (ArgSig("a", False),)),
        ApiElement("mod.Class", "class", (ArgSig("x", False),)),
    }

@pytest.fixture
def sample_new():
    return {
        ApiElement("mod.func", "function", (ArgSig("a", True), ArgSig("b", False))),
        ApiElement("mod.Class", "class", ()),
        ApiElement("mod.new", "function", ()),
    }


def test_diff(sample_old, sample_new):
    result = diff(sample_old, sample_new)
    assert len(result.removed) == 0
    assert len(result.changed) == 2
    assert len(result.added) == 1

    changed_func = next(c for c in result.changed if c[0].qualname == "mod.func")
    assert changed_func[0].arg_sigs != changed_func[1].arg_sigs