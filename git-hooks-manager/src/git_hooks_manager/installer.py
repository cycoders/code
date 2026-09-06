from pathlib import Path

def install_hook(name: str, content: str, git_dir: Path, dry_run: bool = False) -> None:
    hook_path = git_dir / "hooks" / name
    if not dry_run:
        hook_path.write_text(content)
        hook_path.chmod(0o755)