import subprocess
from pathlib import Path
import sys
from typing import List


def profile_run(script: str, output: Path, args: List[str]) -> None:
    """
    Run `python -m cProfile -o output script args`.
    """
    cmd = ["python", "-m", "cProfile", "-o", str(output), script] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5min safeguard
    )

    if result.returncode != 0:
        print(f"❌ Script failed (code {result.returncode}):\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("Profile file empty — cProfile failed silently.")
