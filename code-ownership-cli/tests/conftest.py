import pytest
import subprocess
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_git_repo(monkeypatch):
    monkeypatch.setenv("GIT_DIR", ".git")

@pytest.fixture
def mock_blame_output():
    return """
author John Doe
author-mail john@example.com
author-time 1693526400
author-tz +0000
committer John Doe
committer-mail john@example.com
committer-time 1693526400
committer-tz +0000
summary init
filename main.py
\tdef hello():
\t    pass
boundary
"""
