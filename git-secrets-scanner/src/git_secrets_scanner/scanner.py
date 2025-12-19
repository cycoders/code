import fnmatch
import os
from pathlib import Path
from typing import List, Optional

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

from .detectors import detect_in_text, load_patterns
from .utils import mask_snippet


@dataclass
class Detection:
    detector_id: str
    name: str
    line: int
    snippet: str
    entropy: Optional[float] = None


@dataclass
class SecretHit:
    commit: Optional[str]
    file_path: str
    detection: Detection


def scan_directory(
    path: Path,
    exclude_globs: List[str],
    patterns: List[dict],
    entropy_thresh: float,
    min_length: int,
    allowlist: List[str],
) -> List[SecretHit]:
    """Scan files in directory recursively."""
    hits: List[SecretHit] = []
    for root, _, files in os.walk(path):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(path)
            if any(fnmatch.fnmatch(str(rel_path), glob) for glob in exclude_globs):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                detections = detect_in_text(content, patterns, entropy_thresh, min_length, allowlist)
                for det in detections:
                    hits.append(SecretHit(None, str(rel_path), det))
            except (UnicodeDecodeError, PermissionError, OSError):
                continue  # Binary/image/etc.
    return hits


def scan_git_history(
    repo: git.Repo,
    depth: Optional[int],
    full_history: bool,
    patterns: List[dict],
    entropy_thresh: float,
    min_length: int,
    allowlist: List[str],
    progress: "rich.progress.Progress",
) -> List[SecretHit]:
    """Scan Git history: changed files only."""
    hits: List[SecretHit] = []
    commits = list(repo.iter_commits(all=True, max_count=depth if not full_history else None))
    task = progress.add_task("[cyan]Scanning history...", total=len(commits))

    for commit in commits:
        progress.advance(task)
        parent = commit.parents[0] if commit.parents else None
        diffs = commit.diff(parent)
        for diff in diffs:
            if diff.change_type in ("A", "M", "R") and diff.b_blob:
                try:
                    content = diff.b_blob.data_stream.read().decode("utf-8", errors="ignore")
                    detections = detect_in_text(content, patterns, entropy_thresh, min_length, allowlist)
                    for det in detections:
                        hits.append(SecretHit(commit.hexsha[:8], diff.b_path, det))
                except UnicodeDecodeError:
                    pass
    return hits


def scan(
    path_str: str,
    depth: int,
    full_history: bool,
    exclude_globs: List[str],
    patterns_file: Optional[str],
    entropy_thresh: float,
    min_length: int,
    allowlist: List[str],
) -> List[SecretHit]:
    """Main scan entrypoint."""
    path = Path(path_str).resolve()
    patterns = load_patterns(patterns_file)
    hits: List[SecretHit] = []

    # Check if Git repo
    try:
        repo = git.Repo(path, search_parent_directories=True)
        if not repo.bare:
            from rich.progress import Progress

            with Progress() as progress:
                hist_hits = scan_git_history(
                    repo,
                    depth if not full_history else None,
                    full_history,
                    patterns,
                    entropy_thresh,
                    min_length,
                    allowlist,
                    progress,
                )
                hits.extend(hist_hits)
                # Working tree
                wt_hits = scan_directory(
                    path,
                    exclude_globs,
                    patterns,
                    entropy_thresh,
                    min_length,
                    allowlist,
                )
                for h in wt_hits:
                    h.commit = "working-tree"
                hits.extend(wt_hits)
    except (InvalidGitRepositoryError, GitCommandError):
        pass  # Fall back to dir scan

    # Dir scan if no repo or depth=0
    if depth == 0 or True:  # Always include dir if not handled
        dir_hits = scan_directory(path, exclude_globs, patterns, entropy_thresh, min_length, allowlist)
        for h in dir_hits:
            if h.commit is None:
                h.commit = "working-tree"
        hits.extend(dir_hits)

    return hits