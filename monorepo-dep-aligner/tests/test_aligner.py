import pytest
from pathlib import Path

from monorepo_dep_aligner.aligner import choose_aligned_spec, align_dep_in_package


class TestChooseAlignedSpec:
    def test_max_version(self):
        specs = ["^2.31.0", "2.25.1", ">=2.25.0"]
        assert choose_aligned_spec(specs) == "==2.31.0"

    def test_all_ranges(self):
        specs = ["^1.0.0", ">=1.0.0,<2.0"]
        assert choose_aligned_spec(specs) == "^1.0.0"  # most common fallback

    def test_invalid_versions(self):
        specs = ["invalid", "url"]
        assert choose_aligned_spec(specs) == "invalid"


class TestAlignDep:
    def test_poetry_update(self, tmp_path: Path):
        p = tmp_path / "pyproject.toml"
        p.write_text('[tool.poetry.dependencies]\nfoo = "1.0"\n')
        updated = align_dep_in_package(p, "foo", "2.0")
        assert updated
        assert '"2.0"' in p.read_text()

    def test_pep621(self, tmp_path: Path):
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\ndependencies = {foo = "1.0"}\n')
        updated = align_dep_in_package(p, "foo", "2.0")
        assert updated
        assert '"2.0"' in p.read_text()

    def test_dry_run(self, tmp_path: Path):
        p = tmp_path / "pyproject.toml"
        orig = p.read_text()
        align_dep_in_package(p, "foo", "2.0", dry_run=True)
        assert p.read_text() == orig  # no change

    def test_backup(self, tmp_path: Path):
        p = tmp_path / "pyproject.toml"
        p.write_text("content")
        align_dep_in_package(p, "foo", "2.0", dry_run=False)
        assert (tmp_path / "pyproject.toml.bak").exists()