from pathlib import Path

def load_sbom(path: Path):
    """Load and normalize CycloneDX or SPDX SBOM."""
    # production-grade streaming parser would live here
    return {"components": []}