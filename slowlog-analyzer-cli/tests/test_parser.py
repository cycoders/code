import pytest
from slowlog_analyzer_cli.parser import extract_postgres, parse_mysql
from slowlog_analyzer_cli.models import SlowQuery


@pytest.fixture
def postgres_sample():
    return "2024-04-01 12:00:00.123 UTC [1234] user@db LOG:  duration: 150.5 ms  execute 567: select * from users where id = $1"


@pytest.fixture
def mysql_sample_lines():
    return [
        "# Time: 2024-04-01T12:00:00.123456Z",
        "# User@Host: user[db] @ localhost []",
        "# Query_time: 0.150  Lock_time: 0.000 Rows_sent: 1  Rows_examined: 1000",
        "SET timestamp=1711982400;",
        "select * from users where id = 123;",
    ]


def test_extract_postgres(postgres_sample):
    q = extract_postgres(postgres_sample)
    assert q is not None
    assert q.duration_ms == 150.5
    assert q.user == "user"
    assert q.database == "db"
    assert "select * from users" in q.query


def test_parse_mysql(mysql_sample_lines):
    queries = list(parse_mysql(iter(mysql_sample_lines)))
    assert len(queries) == 1
    q = queries[0]
    assert q.duration_ms == 150.0
    assert q.user == "user"
    assert q.database == "db"
    assert "select * from users" in q.query


def test_invalid_line():
    assert extract_postgres("normal log line") is None
