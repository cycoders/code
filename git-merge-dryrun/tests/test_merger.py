import pytest
from pathlib import Path
from git_merge_dryrun.merger import (
    get_merge_base,
    detect_conflicts,
    get_incoming_commits,
    get_current_graph,
)


def test_get_merge_base(git_repo: Path):
    base = get_merge_base(git_repo, "branch1", "branch2")
    assert base.startswith("0")  # initial commit hash starts with known


def test_detect_conflicts(git_repo: Path):
    base = get_merge_base(git_repo, "branch1", "branch2")
    conflicts = detect_conflicts(git_repo, base, "branch1", "branch2")
    assert "file.txt" in conflicts
    assert len(conflicts) == 1  # only file.txt conflicts


def test_no_conflicts(git_repo: Path):
    # branch2 has extra file, no conflict
    base = get_merge_base(git_repo, "main", "branch2")
    conflicts = detect_conflicts(git_repo, base, "main", "branch2")
    assert conflicts == []


def test_get_incoming_commits(git_repo: Path):
    incoming = get_incoming_commits(git_repo, "main", "branch2")
    assert len(incoming) == 2  # two commits on branch2
    assert "add newfile" in " ".join(incoming)


def test_get_current_graph(git_repo: Path):
    graph = get_current_graph(git_repo)
    assert "*" in graph  # graph chars
    assert "branch2" in graph  # decorate