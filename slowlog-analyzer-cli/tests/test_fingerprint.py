import pytest
from slowlog_analyzer_cli.fingerprint import fingerprint


@pytest.mark.parametrize(
    "q1, q2, expected_same",
    [
        ("SELECT * FROM users WHERE id = 123", "select * from users where id = 456", True),
        ("SELECT * FROM 'test'", "select * from 'other'", True),
        ("/* comment */ SELECT 1", "SELECT 1", True),
        ("UPDATE users SET x=1.23 WHERE y=0xFF", "update users set x=? where y=?", True),
    ],
)
def test_fingerprint_consistent(q1, q2, expected_same):
    fp1 = fingerprint(q1)
    fp2 = fingerprint(q2)
    assert (fp1 == fp2) == expected_same
    assert len(fp1) == 12


def test_fingerprint_unique():
    fp1 = fingerprint("SELECT * FROM a")
    fp2 = fingerprint("SELECT * FROM b")
    assert fp1 != fp2
