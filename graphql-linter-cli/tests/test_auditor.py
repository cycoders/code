import pytest
from ariadne import make_executable_schema, load_schema_from_string
from graphql_linter_cli.auditor import Auditor


@pytest.fixture
def simple_schema():
    sdl = """
    type Query {
      hello: String
    }
    """
    return make_executable_schema(sdl)


def test_auditor_no_issues(simple_schema):
    auditor = Auditor(simple_schema)
    issues = auditor.run()
    assert len(issues) == 0


def test_auditor_ignore_rule(simple_schema):
    auditor = Auditor(simple_schema, ignore_rules={"type-pascal-case"})
    issues = auditor.run()
    # No issues anyway