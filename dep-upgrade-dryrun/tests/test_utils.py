import pytest
from upgrade_dryrun.utils import bump_type


@pytest.mark.parametrize(
    "old_ver, new_ver, expected",
    [
        ("1.0.0", "1.0.1", "patch"),
        ("1.0.0", "1.1.0", "minor"),
        ("1.0.0", "2.0.0", "major"),
        ("1.2.3", "1.2.3", "same"),
        ("v1.0.0", "1.0.1", "unknown"),
        ("1.0.0-alpha", "1.0.1", "patch"),
    ],
)
def test_bump_type(old_ver: str, new_ver: str, expected: str):
    assert bump_type(old_ver, new_ver) == expected
