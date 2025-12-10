import re
from typing import List

from git import Repo
from git.exc import InvalidGitRepositoryError

from .types import Commit
from .config import DEFAULT_CONFIG


CONVENTIONAL_TYPES = set(DEFAULT_CONFIG["type_to_section"].keys())

_PATTERN = re.compile(
    r"^([a-z]+)(?:\(([^)]+)\))?(!)?:\s*(.*)", re.IGNORECASE
)


class ParserError(Exception):
    """Custom parser exception."""


class NoConventionalCommitsError(ParserError):
    """No commits matched conventional format."""


def parse_commits(repo_path: str, since: str, until: str) -> List[Commit]:
    """Parse conventional commits from git range."""
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as exc:
        raise ParserError(f"Invalid git repo: {repo_path}") from exc

    rev_range = f"{since.strip()}..{until.strip()}"
    git_commits = list(repo.iter_commits(rev_range, first_parent=True))

    parsed: List[Commit] = []
    for gc in git_commits:
        msg = gc.message.strip()
        lines = msg.splitlines()
        subject = lines[0]
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""

        match = _PATTERN.match(subject)
        if not match:
            continue

        ctype, scope, bang, title = match.groups()
        ctype = ctype.lower()
        if ctype not in CONVENTIONAL_TYPES:
            continue

        breaking = bool(bang) or "BREAKING CHANGE" in body.upper()

        parsed.append(
            Commit(
                sha=gc.hexsha,
                type_=ctype,
                scope=scope or None,
                title=title.strip(),
                breaking=breaking,
            )
        )

    if not parsed:
        raise NoConventionalCommitsError(
            f"No conventional commits in {rev_range}"
        )

    return parsed