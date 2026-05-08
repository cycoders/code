from pathlib import Path
from unicode_normalizer_cli.scanner import scan_for_normalization, is_text_file


def test_is_text_file(tmp_path: Path):
    text_file = tmp_path / "test.py"
    text_file.write_text("hello")
    assert is_text_file(text_file)

    binary_file = tmp_path / "binary"
    binary_file.write_bytes(b"\x00data")
    assert not is_text_file(binary_file)


def test_scan_detects(tmp_git_repo):
    root, _ = tmp_git_repo
    issues = scan_for_normalization(root, "NFC")
    assert len(issues) == 2
    assert any("name_needs" in issue for issue in issues.values())
    assert any("content_needs" in issue for issue in issues.values())


def test_scan_no_issues(tmp_path: Path):
    (tmp_path / "norm.py").write_text("café")
    issues = scan_for_normalization(tmp_path, "NFC")
    assert len(issues) == 0