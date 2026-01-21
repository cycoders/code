import pytest
from sqlglot import parse_one, Dialects
from db_migration_auditor.rules import RULES
from db_migration_auditor.models import Issue


@pytest.mark.parametrize("rule_idx, sql, dialect, expected_codes", [
    (0, "DROP TABLE users;", Dialects.POSTGRES, ["no_drop_table"]),
    (1, "ALTER TABLE users DROP COLUMN email;", Dialects.MYSQL, ["no_drop_column"]),
    (4, "ALTER TABLE users ALTER COLUMN name DROP NOT NULL;", Dialects.POSTGRES, ["drop_not_null_no_default"]),
    (5, "CREATE INDEX idx_name ON users(name);", Dialects.POSTGRES, ["no_concurrent_index"]),
])
def test_rules(rule_idx, sql, dialect, expected_codes):
    stmt = parse_one(sql, dialect=dialect)
    all_issues = []
    for rule in RULES:
        issues = rule(stmt, "test.sql")
        if issues:
            all_issues.extend(issues)
    codes = [i.code for i in all_issues]
    assert set(expected_codes).issubset(set(codes))


def test_no_false_positives():
    safe_sql = "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();"
    stmt = parse_one(safe_sql, dialect=Dialects.POSTGRES)
    issues = []
    for rule in RULES:
        rule_issues = rule(stmt, "test.sql")
        if rule_issues:
            issues.extend(rule_issues)
    assert len(issues) == 0