import pytest
from pathlib import Path

from git_bloat_analyzer import analyzer
from git_bloat_analyzer.types import BlobInfo, RepoStats


def test_get_repo_stats(mini_repo: Path):
    stats = analyzer.get_repo_stats(mini_repo)
    assert isinstance(stats, RepoStats)
    assert stats.disk_usage > 0
    assert "size-pack" in stats.count_objects


def test_get_large_blobs(mini_repo: Path):
    blobs = analyzer.get_large_blobs(mini_repo, top_n=10, min_size_kb=1000)
    assert len(blobs) >= 1
    large_blob = blobs[0]
    assert large_blob.path == "large.bin"
    assert large_blob.size >= 5 * 1024 * 1024
    assert "MiB" in large_blob.size_str


def test_get_large_blobs_no_blobs(empty_repo: Path):
    blobs = analyzer.get_large_blobs(empty_repo, min_size_kb=1000)
    assert len(blobs) == 0


def test_get_pack_stats(mini_repo: Path):
    packs = analyzer.get_pack_stats(mini_repo)
    # May be empty initially
    for pack in packs:
        assert pack.compression_ratio >= 0


def test_human_size():
    assert analyzer.human_size(512) == " 512.0 B"
    assert analyzer.human_size(1024 * 1024 * 2 + 512) == "   2.0 MiB"