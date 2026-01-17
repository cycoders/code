import pytest
from git_worktree_manager.worktree import parse_worktree_list, get_worktree_status
from pathlib import Path

sample_porcelain = """worktree /repo\nheadrefs refs/heads/main\n\nworktree /repo/wt1\nheadrefs refs/heads/feat/x\nlocked invalid"""

def test_parse_worktree_list():
    wts = parse_worktree_list(sample_porcelain)
    assert len(wts) == 2
    assert wts[0]["path"] == "/repo"
    assert wts[0]["headrefs"] == "refs/heads/main"
    assert wts[1]["locked"] == "invalid"

def test_get_worktree_status(mocker):
    mocker.patch("git_worktree_manager.worktree.run_git", return_value="# branch.ab +2 -0 origin/main\nM file.py")
    status = get_worktree_status(Path="/tmp")
    assert status["branch"] == "main"
    assert status["ahead"] == 2
    assert status["behind"] == 0
    assert status["dirty"] == 1