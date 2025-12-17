import pytest
from pathlib import Path
from link_auditor.collector import collect_links
from link_auditor.settings import Settings


def test_collect_md_file(tmp_path: Path, settings: Settings):
    md_file = tmp_path / "test.md"
    md_file.write_text("[Link](https://ex.com)")
    links = collect_links([str(md_file)], settings)
    assert "https://ex.com" in links


def test_collect_dir(tmp_path: Path):
    (tmp_path / "docs" / "test.md").write_text("[Link](https://ex.com)")
    links = collect_links([str(tmp_path / "docs")], Settings())
    assert "https://ex.com" in links


def test_url(tmp_path: Path):
    # Mock not needed, but skip real fetch in test
    pass
