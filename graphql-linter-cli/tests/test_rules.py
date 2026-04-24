import pytest
from ariadne import load_schema_from_string, make_executable_schema
from graphql_linter_cli.rules.naming import check_naming
from graphql_linter_cli.rules.deprecations import check_deprecations


def test_naming_pascal_fail():
    sdl = "type user { id: ID }"
    schema = load_schema_from_string(sdl)
    issues = check_naming(schema)
    assert len(issues) == 1
    assert issues[0]["rule"] == "type-pascal-case"


def test_deprecations_no_reason():
    sdl = """
    type Query {
      old: String @deprecated
    }
    """
    schema = load_schema_from_string(sdl)
    issues = check_deprecations(schema)
    assert len(issues) == 1
    assert issues[0]["rule"] == "deprecated-no-reason"

# More tests for other rules...
