import pytest
from git_secrets_scanner.utils import shannon_entropy


@pytest.mark.parametrize(
    "data, expected",
    [
        ("aaaaa", 0.0),
        ("abc", pytest.approx(1.58496)),
        ("a" * 20 + "Z" * 20, pytest.approx(1.0)),
        ("SG.dGVzdF9zZWNyZXRfdG9rZW4_1234567890abcdef==", pytest.approx(4.7)),
    ],
)
def test_shannon_entropy(data: str, expected: float):
    assert shannon_entropy(data) == expected