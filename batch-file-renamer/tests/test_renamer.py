import pytest
import time
from pathlib import Path
from batch_file_renamer.renamer import (
    apply_rule,
    preview_renames,
    get_candidate_files,
    sort_key,
)


@pytest.mark.parametrize(
    "current, rule, extra, expected",
    [
        ("old.txt", {"type": "prefix", "value": "new_"}, {}, "new_old.txt"),
        ("file.jpg", {"type": "suffix", "value": "_backup"}, {}, "file.jpg_backup"),
        (
            "IMG_1234.jpg",
            {"type": "regex", "pattern": r"IMG_(\d+)", "replacement": "renamed_\1"},
            {},
            "renamed_1234.jpg",
        ),
        (
            "photo.jpg",
            {
                "type": "counter",
                "fmt": "{:03d}_",
                "position": "prefix",
            },
            {"index": 4},
            "005_photo.jpg",
        ),
        (
            "doc.txt",
            {"type": "timestamp", "fmt": "%Y%m", "stat": "mtime"},
            {"stat": os.stat("somefile")},  # mock
            "202501_doc.txt",  # depends on time, but tests format
        ),
    ],
)
def test_apply_rule(current, rule, extra, expected):
    result = apply_rule(current, rule, extra)
    # timestamp approximate
    if "timestamp" in rule["type"]:
        assert result.startswith(expected[:6])
    else:
        assert result == expected


def test_chain_rules(tmp_path: Path):
    (tmp_path / "test.jpg").touch()
    rules = [
        {"type": "regex", "pattern": ".*\\.jpg", "replacement": "png"},
        {"type": "prefix", "value": "new_"},
    ]
    extra = {"index": 0, "stat": (tmp_path / "test.jpg").stat()}
    current = "test.jpg"
    for rule in rules:
        current = apply_rule(current, rule, extra)
    assert current == "new_png"


def test_get_candidate_files(tmp_path: Path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.jpg").touch()
    (tmp_path / ".git").touch()
    files = get_candidate_files(tmp_path, include=["*.txt"], exclude=[".*"])
    assert len(files) == 1
    assert files[0].name == "a.txt"


def test_sort_key(tmp_path: Path):
    p1 = tmp_path / "z.txt"
    p2 = tmp_path / "a.txt"
    p1.touch()
    p2.touch()
    assert sort_key(p1, "name") > sort_key(p2, "name")


def test_preview_conflict(tmp_path: Path):
    (tmp_path / "test.txt").touch()
    (tmp_path / "new.txt").touch()
    rules = [{"type": "prefix", "value": "new_"}]
    renames = preview_renames(tmp_path, rules, "name", None, None, None)
    assert any(r["status"] == "conflict" for r in renames)