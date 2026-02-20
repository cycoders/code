import pytest
from unittest.mock import MagicMock
from pathlib import Path
from git_lfs_migrator.scanner import collect_large_file_stats
from git_lfs_migrator.utils import run_git


@pytest.mark.parametrize(
    "threshold_mb, expected_stats",
    [
        (
            5.0,
            {
                ".png": {"count": 2, "total_size": 24000000, "paths": {"assets/image.png"}},
                ".jpg": {"count": 1, "total_size": 8000000, "paths": {"assets/other.jpg"}},
            },
        ),
    ],
)
def test_collect_large_file_stats(mocker, tmp_path: Path, threshold_mb, expected_stats):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    mock_run = mocker.patch("git_lfs_migrator.scanner.run_git")
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="commit1\ncommit2"),
        MagicMock(returncode=0, stdout="100644 blob abc123 12000000\tassets/image.png\n100644 blob def456 8000000\tassets/other.jpg"),
        MagicMock(returncode=0, stdout="100644 blob abc123 12000000\tassets/image.png"),
    ]

    stats = collect_large_file_stats(repo_path, threshold_mb)

    assert stats == expected_stats
    mock_run.assert_called()


def test_collect_large_file_stats_no_large_files(mocker, tmp_path: Path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    mocker.patch(
        "git_lfs_migrator.scanner.run_git",
        return_value=MagicMock(returncode=0, stdout="commit1"),
    )

    stats = collect_large_file_stats(repo_path, threshold_mb=100.0)
    assert stats == {}
