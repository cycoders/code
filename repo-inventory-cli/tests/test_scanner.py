import os
from pathlib import Path

import pytest

from repo_inventory_cli.scanner import scan_repos
from repo_inventory_cli.config import DEFAULT_CONFIG


class TestScanner:
    def test_finds_repo(self, sample_repo: Path):
        repos = scan_repos([str(sample_repo.parent)], DEFAULT_CONFIG["excludes"])
        assert len(repos) == 1
        assert repos[0].path.endswith("testrepo")

    def test_skips_non_repo(self, tmp_path: Path):
        non_repo = tmp_path / "norepo"
        non_repo.mkdir()
        repos = scan_repos([str(tmp_path)], [])
        assert len(repos) == 0

    def test_prunes_excludes(self, tmp_path: Path, sample_repo: Path):
        venv_dir = tmp_path / ".venv" / "testrepo"
        venv_dir.mkdir(parents=True)
        (venv_dir / ".git").mkdir()
        repos = scan_repos([str(tmp_path)], ["**/.venv/**"])
        assert len(repos) == 0

    def test_multiple_paths(self, sample_repo: Path, orphaned_repo: Path):
        paths = [str(sample_repo.parent), str(orphaned_repo.parent)]
        repos = scan_repos(paths, [])
        assert len(repos) == 2
