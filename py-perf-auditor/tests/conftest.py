import os
import sys

from pathlib import Path

# Add src to path for tests
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / "src"))

os.environ["PYTHONPATH"] = ":".join(sys.path)