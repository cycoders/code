import subprocess
from pathlib import Path

def run_test(path: Path) -> bool:
    """Execute test and return True if it still fails."""
    result = subprocess.run(
        ["python", "-m", "pytest", str(path)],
        capture_output=True, text=True
    )
    return result.returncode != 0