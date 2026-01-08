from py_api_diff.models import ApiElement, ArgSig


def test_api_element_hashable():
    el1 = ApiElement("mod.func", "function", (ArgSig("a", False),))
    el2 = ApiElement("mod.func", "function", (ArgSig("a", False),))
    assert el1 == el2
    assert hash(el1) == hash(el2)


def test_api_element_invalid_kind():
    from pytest import raises
    with raises(ValueError):
        ApiElement("mod.x", "invalid", ())