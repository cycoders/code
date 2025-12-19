import pytest
from git_secrets_scanner.scanner import scan_directory, scan_git_history, SecretHit


def test_scan_directory_clean(clean_temp_dir):
    hits = scan_directory(clean_temp_dir, [], [], 3.5, 20, [])
    assert len(hits) == 0


def test_scan_git_repo_detects_secrets(temp_repo):
    import git
    repo = git.Repo(temp_repo)
    from rich.progress import Progress
    hits = scan_git_history(repo, 10, False, [], 3.5, 20, [], Progress())
    assert len(hits) >= 2  # AWS + entropy
    assert any("AKIA" in h.detection.snippet for h in hits)
    assert any(h.detection.detector_id == "high_entropy" for h in hits)