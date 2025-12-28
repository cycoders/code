import pytest
from pathlib import Path
from conventional_commit_linter.config import load_config, LintConfig


@pytest.fixture
def tmp_git_root(tmp_path: Path):
    git_path = tmp_path / ".git"
    git_path.mkdir()
    (tmp_path / "test.txt").touch()
    return tmp_path


class TestConfig:
    def test_default(self, tmp_git_root):
        cfg = load_config(tmp_git_root)
        assert cfg.types == [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "build",
            "ci",
            "chore",
            "revert",
        ]
        assert cfg.max_subject_length == 50

    def test_pyproject(self, tmp_git_root: Path):
        pyproject = tmp_git_root / "pyproject.toml"
        pyproject.write_text(
            """
[tool.conventional-commit-linter]
types = ["custom", "feat"]
max_subject_length = 100
scopes = ["api"]
        """
        )
        cfg = load_config(tmp_git_root)
        assert "custom" in cfg.types
        assert cfg.max_subject_length == 100
        assert cfg.scopes == ["api"]

    def test_yaml(self, tmp_git_root: Path):
        yaml_path = tmp_git_root / ".conventional-commit-lintrc.yaml"
        yaml_path.write_text("types: [yaml-type]\nmax_line_length: 120")
        cfg = load_config(tmp_git_root)
        assert "yaml-type" in cfg.types
        assert cfg.max_line_length == 120

    def test_pyproject_over_yaml(self, tmp_git_root: Path):
        pyproject = tmp_git_root / "pyproject.toml"
        pyproject.write_text("[tool.conventional-commit-linter]\ntypes=[pyproject]")
        yaml_path = tmp_git_root / ".conventional-commit-lintrc.yaml"
        yaml_path.write_text("types: [yaml]")
        cfg = load_config(tmp_git_root)
        assert "pyproject" in cfg.types  # pyproject first
        assert "yaml" not in cfg.types
