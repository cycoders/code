from typing import List

from .config import LintConfig
from .parser import parse_commit_message


class LintResult:
    """Collection of lint errors."""

    def __init__(self, errors: List[str]):
        self.errors = errors

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


class CommitLinter:
    """
    Validates commit message against config.

    >>> config = LintConfig(types=["feat"])
    >>> linter = CommitLinter(config)
    >>> linter.lint("feat: ok").valid
    True
    """

    def __init__(self, config: LintConfig):
        self.config = config

    def lint(self, message: str) -> LintResult:
        errors: List[str] = []
        try:
            parsed = parse_commit_message(message)
        except ValueError as e:
            return LintResult([f"Parse error: {e}"])

        # Type
        if parsed["type"] not in self.config.types:
            errors.append(
                f"Invalid type '{parsed['type']}'. Allowed: {', '.join(self.config.types)}"
            )

        # Scope
        scope = parsed["scope"]
        if scope is not None:
            allowed_scopes = self.config.scopes or ["any"]
            if scope not in allowed_scopes:
                errors.append(
                    f"Invalid scope '{scope}'. Allowed: {', '.join(allowed_scopes)}"
                )

        # Subject
        subject = parsed["subject"]
        if not subject:
            errors.append("Subject cannot be empty")
        if len(subject) > self.config.max_subject_length:
            errors.append(
                f"Subject too long: {len(subject)} chars > {self.config.max_subject_length}"
            )
        if subject and subject[0].isupper():
            errors.append("Subject must start with lowercase (imperative mood)")
        if subject.endswith("."):
            errors.append("Subject must not end with period")

        # Body line lengths
        for line_num, line in enumerate(parsed["body"].splitlines(), start=2):
            if len(line) > self.config.max_line_length:
                errors.append(
                    f"Body line {line_num} too long: {len(line)} > {self.config.max_line_length}"
                )

        return LintResult(errors)
