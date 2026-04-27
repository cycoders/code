import pytest
from pathlib import Path

@pytest.fixture
def sample_porcelain() -> str:
    return """
commit abc123def4567890abcdef1234567890abcde
author John Doe <john@example.com>
author-mail <john@example.com>
author-time 1704067200
author-tz -28800
committer John Doe <john@example.com>
committer-mail <john@example.com>
committer-time 1704067200
committer-tz -28800
filename test.py
test.py abc123def4567890abcdef1234567890abcde abc123def4567890abcdef1234567890abcde def parse():

test.py fedcba9876543210fedcba9876543210fedcba  fedcba9876543210fedcba9876543210fedcba    print("hello")

boundary
commit 111222333444555666777888999000aaaabbbb
"""
