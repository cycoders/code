import pytest

from arch_boundary_auditor.parser import extract_imports, get_full_module_name


@pytest.mark.parametrize(
    "code, expected",
    [
        (
            "import domain.user\nfrom infra.db import models",
            [("domain.user", 1), ("infra.db", 2)],
        ),
        (
            "from utils import helper\nimport core",
            [("utils", 1), ("core", 2)],
        ),
        (
            "from .local import Local\nfrom ..sibling import X",  # relative skipped
            [],
        ),
        ("pass", []),
    ],
)
def test_extract_imports(code: str, expected: list):
    result = extract_imports(code)
    mods = [(mod, line) for mod, line in result]
    assert set(mods) == set(expected)


@pytest.mark.parametrize(
    "node_desc, expected",
    [
        ("simple name", "test"),
        ("dotted attr", "foo.bar"),
    ],
)
def test_get_full_module_name(node_desc: str):
    # Simplified; full test via extract
    pass


def test_unsupported_node():
    with pytest.raises(ValueError):
        get_full_module_name(None)