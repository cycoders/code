from datetime import datetime
import re

from .models import GitCommit, GitFileChange


def parse_git_log(raw_output: str) -> list[GitCommit]:
    """
    Parse git log --numstat --pretty=format:%H\t%at\t%an\t%s output.

    Returns list of GitCommit with changes.
    """
    commits: list[GitCommit] = []
    current_changes: list[GitFileChange] = []
    current_commit: GitCommit | None = None

    for line in raw_output.splitlines():
        line = line.rstrip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) == 4 and len(parts[0]) == 40 and re.match(r"^[0-9a-f]{40}$", parts[0]):
            # New commit line
            if current_commit:
                current_commit.changes = current_changes
                commits.append(current_commit)
            current_changes = []
            sha, ts_str, author, summary = parts
            try:
                ts = int(ts_str)
            except ValueError:
                continue
            timestamp = datetime.utcfromtimestamp(ts)
            current_commit = GitCommit(sha, timestamp, author, summary)
        elif len(parts) == 3 and current_commit is not None:
            # File change line
            path, ins_str, del_str = parts
            try:
                insertions = int(ins_str) if ins_str != "-" else 0
                deletions = int(del_str) if del_str != "-" else 0
            except ValueError:
                continue
            current_changes.append(GitFileChange(path.rstrip(), insertions, deletions))

    # Append last commit
    if current_commit:
        current_commit.changes = current_changes
        commits.append(current_commit)

    return commits
