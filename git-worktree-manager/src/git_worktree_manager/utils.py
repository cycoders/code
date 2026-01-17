import subprocess
from typing import Any

def run_git(*args: str, cwd: str | None = None) -> str:
    """Execute git command safely, raise on error."""
    cmd = ["git"] + [str(arg) for arg in args]
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"git {' '.join(cmd)} failed (code {exc.returncode}):\n{exc.stderr or exc.stdout}"
        ) from exc