import glob
from pathlib import Path
from typing import List

from .cli import ResizeMode, DiffMode
from .differ import SimilarityResult, compute_similarity


def batch_compare(
    before_dir: Path,
    after_dir: Path,
    threshold: float,
    resize: ResizeMode,
    mode: DiffMode,
) -> List[SimilarityResult]:
    """Compare paired images."""

    before_files = set(p.stem for p in before_dir.glob("*.{png,jpg,jpeg,gif}") if p.is_file())
    after_files = set(p.stem for p in after_dir.glob("*.{png,jpg,jpeg,gif}") if p.is_file())

    common = sorted(before_files & after_files)

    results = []
    for stem in common:
        img1 = before_dir / f"{stem}.png"  # Assume png, fallback in glob
        # Real: find matching ext
        for ext in ["png", "jpg", "jpeg"]:
            p1 = before_dir / f"{stem}.{ext}"
            p2 = after_dir / f"{stem}.{ext}"
            if p1.exists() and p2.exists():
                img1, img2 = p1, p2
                break
        else:
            continue

        result = compute_similarity(str(img1), str(img2), resize)
        result.basename = stem
        results.append(result)

    return results
