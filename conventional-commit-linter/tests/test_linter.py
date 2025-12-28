import pytest
from conventional_commit_linter.linter import CommitLinter, LintResult
from conventional_commit_linter.config import LintConfig


@pytest.fixture
def default_config():
    return LintConfig()


@pytest.fixture
def strict_config():
    return LintConfig(types=["feat"], scopes=["ui"], max_subject_length=10)


class TestCommitLinter:
    def test_valid(self, default_config):
        linter = CommitLinter(default_config)
        result = linter.lint("feat(ui): add thing")
        assert isinstance(result, LintResult)
        assert result.valid

    def test_invalid_type(self, default_config):
        linter = CommitLinter(default_config)
        result = linter.lint("invalid: msg")
        assert not result.valid
        assert "type 'invalid'" in " ".join(result.errors)

    def test_scope_invalid(self, strict_config):
        linter = CommitLinter(strict_config)
        result = linter.lint("feat(api): ok")  # api != ui
        assert not result.valid
        assert "scope 'api'" in " ".join(result.errors)

    def test_subject_too_long(self, default_config):
        long_subject = "a" * 60
        linter = CommitLinter(default_config)
        result = linter.lint(f"feat: {long_subject}")
        assert not result.valid
        assert "too long" in " ".join(result.errors)

    def test_subject_uppercase(self, default_config):
        linter = CommitLinter(default_config)
        result = linter.lint("feat: Add thing")
        assert not result.valid
        assert "lowercase" in " ".join(result.errors)

    def test_subject_period(self, default_config):
        linter = CommitLinter(default_config)
        result = linter.lint("feat: ends.")
        assert not result.valid
        assert "period" in " ".join(result.errors)

    def test_body_long_line(self, default_config):
        long_line = "a" * 80
        msg = f"feat: ok\n{long_line}"
        linter = CommitLinter(default_config)
        result = linter.lint(msg)
        assert not result.valid
        assert "line 2 too long" in " ".join(result.errors)
