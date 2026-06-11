import pytest
from db_url_auditor.parser import parse_url, ParseError

def test_valid_postgres():
    r = parse_url("postgresql://user@host/db")
    assert r.scheme == "postgresql"

def test_invalid_scheme():
    with pytest.raises(ParseError):
        parse_url("ftp://host")