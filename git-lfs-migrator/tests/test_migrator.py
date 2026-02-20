import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from git_lfs_migrator.migrator import perform_migration, check_git_lfs_installed


def test_perform_migration(mocker, tmp_path: Path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    mocker.patch(
        "git_lfs_migrator.migrator.run_git",
        return_value=MagicMock(returncode=0, stdout="Migration preview: 1.2GB saved"),
    )

    output = perform_migration(repo_path, "*.png", dry_run=True)
    assert "saved" in output


@pytest.mark.parametrize("raises", [True, False])
def test_check_git_lfs_installed(mocker, tmp_path: Path, raises):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    mock_run = mocker.patch("git_lfs_migrator.migrator.run_git")
    mock_run.side_effect = subprocess.CalledProcessError(1, "git") if raises else MagicMock(returncode=0)

    if raises:
        with pytest.raises(RuntimeError):
            check_git_lfs_installed(repo_path)
    else:
        check_git_lfs_installed(repo_path)
