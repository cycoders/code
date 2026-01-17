import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture(autouse=True)
def mock_git(mocker):
    def mock_run_git(*args, **kwargs):
        cwd = kwargs.get("cwd")
        if "worktree" in args[0] and "list" in args[1:]:
            return """worktree /tmp/repo\nheadrefs refs/heads/main\n\nworktree /tmp/repo/worktrees/feat-test\nheadrefs refs/heads/feat/test"""
        if "status" in args[0]:
            return "# branch.feat/test +0 -1 origin/feat/test\n1 U file.txt"
        if "rev-parse" in args[0]:
            return "abc1234"
        if "log" in args[0]:
            return "1720000000"
        raise RuntimeError("Mock git fail")
    mocker.patch("git_worktree_manager.worktree.run_git", side_effect=mock_run_git)