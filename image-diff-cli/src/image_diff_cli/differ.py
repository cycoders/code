import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from rich.progress import track

from .image_utils import load_image, resize_images, ResizeMode
from .metrics import ssim, psnr, mse
from .renderer import compute_normalized_diff, save_visualization, DiffMode


@dataclass
class SimilarityResult:
    basename: str
    ssim_score: float
    psnr_score: float
    mse_score: float
    img1_shape: tuple
    img2_shape: tuple
    max_diff: float  # 1 - ssim

    @property
    def ssim(self) -> float:
        return self.ssim_score

    @property
    def psnr(self) -> float:
        return self.psnr_score

    @property
    def mse(self) -> float:
        return self.mse_score

    def save_visualizations(self, prefix_path: Path, mode: DiffMode):
        """Save all diff modes for completeness."""
        # Note: img1/img2 stored as attrs? For simplicity, recompute
        # In prod, cache them.
        diff_norm = compute_normalized_diff(self._img1, self._img2)  # Assume stored
        save_visualization(self._img1, self._img2, diff_norm, str(prefix_path.with_suffix(".png")), mode)

    def to_json(self) -> str:
        return json.dumps({
            "id": str(uuid.uuid4()),
            "basename": self.basename,
            "ssim": self.ssim,
            "psnr": self.psnr,
            "mse": self.mse,
            "max_diff": self.max_diff,
            "pass": self.max_diff <= 0.02,  # Default
        })

    def __post_init__(self):
        self.max_diff = 1 - self.ssim_score


def compute_similarity(
    img1_path: str,
    img2_path: str,
    resize: ResizeMode = "fit",
    max_size: Optional[int] = 2048,
) -> SimilarityResult:
    """Core comparison logic."""

    img1 = load_image(img1_path, max_size)
    img2 = load_image(img2_path, max_size)

    img1, img2 = resize_images(img1, img2, resize)

    s = ssim(img1, img2)
    p = psnr(img1, img2)
    m = mse(img1, img2)

    # Store for viz
    result = SimilarityResult(
        basename=Path(img1_path).stem,
        ssim_score=s,
        psnr_score=p,
        mse_score=m,
        img1_shape=img1.shape,
        img2_shape=img2.shape,
    )
    result._img1 = img1
    result._img2 = img2  # Hack for dataclass
    return result
