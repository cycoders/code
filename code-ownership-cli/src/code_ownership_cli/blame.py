import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Iterator
from datetime import datetime
import logging
from rich.progress import Progress, SpinnerColumn, TextColumn

LineBlame = Tuple[str, datetime]

async def parse_blame_porcelain(output: str) -> Iterator[LineBlame]:
    """Parse git blame --porcelain output into (author, datetime) per line."""
    lines = output.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("author "):
            author = line[7:].rstrip()
            i += 1
            # Skip author-mail
            i += 1
            if i < len(lines) and lines[i].startswith("author-time "):
                timestamp = int(lines[i][12:])
                author_time = datetime.fromtimestamp(timestamp)
                i += 1
                # Skip tz, committer (4 lines), summary, filename
                i += 6
                # Content lines
                while i < len(lines) and lines[i].startswith("\t"):
                    yield (author, author_time)
                    i += 1
            else:
                i += 1  # Skip malformed
        else:
            i += 1


def collect_blame_data(
    repo: Path,
    exts: List[str] = None,
    since: Optional[str] = None,
    path: Path = Path("."),
) -> List[LineBlame]:
    """Collect blame data from repo."""
    repo = repo.resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"Not a git repo: {repo}")

    since_dt = datetime.min if not since else datetime.strptime(since, "%Y-%m-%d")

    cmd = ["git", "-C", str(repo), "ls-files", str(path)]
    files_str = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    files = [Path(f).resolve() for f in files_str.split("\n") if f]

    if exts and "*" not in exts:
        files = [f for f in files if f.suffix[1:] in exts]

    all_blame: List[LineBlame] = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Collecting blame...", total=len(files))
        for file_path in files:
            try:
                rel_path = file_path.relative_to(repo)
                cmd = ["git", "-C", str(repo), "blame", "--porcelain", str(rel_path)]
                output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(errors="ignore")
                file_blame = list(parse_blame_porcelain(output))
                recent_blame = [(a, t) for a, t in file_blame if t >= since_dt]
                all_blame.extend(recent_blame)
                progress.advance(task)
            except (subprocess.SubprocessError, UnicodeDecodeError) as e:
                logging.debug(f"Skipped {rel_path}: {e}")
    return all_blame