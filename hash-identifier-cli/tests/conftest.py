import pytest

from hash_identifier_cli.identifier import identify


@pytest.fixture
def sample_md5():
    return "5d41402abc4b2b76b8db0aedd4bf355d"


@pytest.fixture
def sample_sha256():
    return "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"