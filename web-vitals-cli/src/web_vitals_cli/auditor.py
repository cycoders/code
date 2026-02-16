import json
import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from .server import serve_directory, find_free_port
from .parser import parse_lighthouse_json
from .types import LighthouseResult

logger = logging.getLogger(__name__)


def audit_page(
    target: str,
    categories: List[str] = ["performance"],
    timeout: int = 60,
) -> LighthouseResult:
    """Run Lighthouse audit on target (URL or file path)."""
    # Handle local file
    audit_url = target
    if not target.startswith(("http://", "https://")):
        p = Path(target)
        if p.exists() and p.is_file():
            port = find_free_port()
            base_url = serve_directory(str(p.parent), port)
            audit_url = f"{base_url}{p.name}"
            logger.info(f"Serving local file at {audit_url}")

    # Lighthouse cmd
    cat_str = ",".join(categories)
    cmd = [
        "npx",
        "lighthouse",
        audit_url,
        "--output=json",
        "--output-path=-",
        f"--only-categories={cat_str}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
        lh_data = json.loads(result.stdout)
        return parse_lighthouse_json(lh_data)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Lighthouse timed out after {timeout}s")
    except subprocess.CalledProcessError as e:
        logger.error(f"Lighthouse stderr: {e.stderr}")
        raise RuntimeError(f"Lighthouse failed: {e.stderr.strip()}")
    except FileNotFoundError:
        raise RuntimeError(
            "Node.js/npx not found. Install Node: https://nodejs.org/"
        )
    except json.JSONDecodeError:
        raise RuntimeError("Invalid Lighthouse JSON output")


def batch_audit(targets: List[str], **kwargs) -> List[LighthouseResult]:
    """Audit multiple targets."""
    results = []
    for t in targets:
        results.append(audit_page(t, **kwargs))
    return results