import pytest
from pathlib import Path
import os
from datetime import datetime, timedelta, timezone

from git import Repo
from todo_tracker_cli.analyzer import analyze_todos
from todo_tracker_cli.scanner import scan


@pytest.fixture
def git_repo(tmp_path: Path):
    """Temp Git repo with commit."""
    repo_path = tmp_path / 'repo'
    repo_path.mkdir()
    repo = Repo.init(repo_path)

    (repo_path / 'test.py').write_text('# TODO: test')
    repo.index.add(['test.py'])
    commit = repo.index.commit('Add todo')

    return repo_path, repo


def test_analyze_todos(git_repo):
    repo_path, _ = git_repo
    todos = list(scan(repo_path, []))
    analyzed = analyze_todos(todos, str(repo_path))

    assert len(analyzed) == 1
    assert analyzed[0].age_days is not None
    assert 0 <= analyzed[0].age_days <= 1  # Recent commit


def test_no_git(tmp_path: Path, sample_py_file):
    todos = list(scan(tmp_path, []))
    analyzed = analyze_todos(todos, str(tmp_path))
    assert analyzed[0].age_days is None  # No repo