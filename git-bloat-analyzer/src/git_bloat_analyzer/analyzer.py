import subprocess
from pathlib import Path
from typing import List

import git_bloat_analyzer.git_commands as git_cmds
import git_bloat_analyzer.types as types
from git_bloat_analyzer.types import BlobInfo, PackInfo, RepoStats


def human_size(size: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            return f"{size:6.1f} {unit}"
        size /= 1024.0
    return f"{size:6.1f} PiB"


def get_repo_stats(repo_path: Path) -> RepoStats:
    """Parse git count-objects and disk usage."""
    output = git_cmds.run_git(["count-objects", "-vH"], repo_path)
    stats = {}
    for line in output.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            stats[key.strip()] = val.strip()

    git_dir = Path(git_cmds.run_git(["rev-parse", "--git-dir"], repo_path).strip())
    disk_usage = sum(p.stat().st_size for p in git_dir.rglob("*") if p.is_file())

    pack_size = int(stats.get("size-pack", "0").split()[0]) * 1024 if stats.get("size-pack") else 0
    bloat_score = max(0.0, (1.0 - pack_size / disk_usage) * 100) if disk_usage else 0.0

    return RepoStats(
        count_objects=stats,
        disk_usage=disk_usage,
        disk_usage_str=human_size(disk_usage),
        bloat_score=bloat_score,
    )


def get_large_blobs(repo_path: Path, top_n: int = 20, min_size_kb: int = 1024) -> List[BlobInfo]:
    """Find top N largest blobs efficiently via pipe."""
    min_size = min_size_kb * 1024
    rev_cmd = ["git", "-C", str(repo_path), "rev-list", "--objects", "--all"]
    batch_fmt = "%s%x00%s%x00%s%x00%s"
    batch_cmd = ["git", "-C", str(repo_path), "cat-file", f"--batch-check={batch_fmt}", "--stdin"]

    p1 = subprocess.Popen(rev_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p2 = subprocess.Popen(batch_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p1.stdout.close()
    output, stderr = p2.communicate()

    if p2.returncode != 0:
        raise RuntimeError(f"Failed to scan objects: {stderr}")

    blobs = []
    for line in output.splitlines():
        parts = line.split("\x00")
        if len(parts) >= 4:
            obj_type, sha, size_str, rest = parts[:4]
            if obj_type == "blob":
                size = int(size_str)
                if size >= min_size:
                    path = (rest.split("\x00")[0] or "N/A").strip()
                    blobs.append(BlobInfo(sha=sha[:7], path=path, size=size))

    blobs.sort(key=lambda b: b.size, reverse=True)
    top_blobs = blobs[:top_n]

    for blob in top_blobs:
        blob.size_str = human_size(blob.size)

    return top_blobs


def get_pack_stats(repo_path: Path) -> List[PackInfo]:
    """Analyze all .pack files."""
    pack_dir = repo_path / ".git" / "objects" / "pack"
    packs = []
    for pack_file in pack_dir.glob("pack-*.pack"):
        rel_pack = f".git/objects/pack/{pack_file.name}"
        try:
            output = git_cmds.run_git(["verify-pack", "-v", rel_pack], repo_path)
            num_objects = 0
            total_obj_size = 0
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2 and not line.startswith("non ") and not line.startswith("chain "):
                    total_obj_size += int(parts[1])
                    num_objects += 1
            pack_size = pack_file.stat().st_size
            ratio = ((1 - total_obj_size / pack_size) * 100) if pack_size else 0.0
            packs.append(
                PackInfo(
                    pack_file=pack_file.name,
                    pack_size=pack_size,
                    obj_count=num_objects,
                    total_obj_size=total_obj_size,
                    compression_ratio=ratio,
                    pack_size_str=human_size(pack_size),
                    total_obj_size_str=human_size(total_obj_size),
                )
            )
        except RuntimeError:
            continue  # Skip corrupt packs

    packs.sort(key=lambda p: p.pack_size, reverse=True)
    return packs