import numpy as np
from skimage.metrics import structural_similarity as ssim_impl
from typing import Tuple

def ssim(img1: np.ndarray, img2: np.ndarray, **kwargs) -> float:
    """
    Structural Similarity Index (0-1, 1=identical).

    Handles multichannel by averaging grayscale.
    """
    if img1.ndim == 3:
        img1_gray = np.mean(img1, axis=2)
    else:
        img1_gray = img1

    if img2.ndim == 3:
        img2_gray = np.mean(img2, axis=2)
    else:
        img2_gray = img2

    data_range = img2_gray.max() - img2_gray.min()
    if data_range == 0:
        return 1.0

    return ssim_impl(img1_gray, img2_gray, data_range=data_range, **kwargs)

def mse(img1: np.ndarray, img2: np.ndarray) -> float:
    """Mean Squared Error (lower=better)."""
    return float(np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2))

def psnr(img1: np.ndarray, img2: np.ndarray, max_val: float = 255.0) -> float:
    """
    Peak Signal-to-Noise Ratio (higher=better).

    :param max_val: Max pixel value (255 for 8-bit).
    """
    mse_val = mse(img1, img2)
    if mse_val == 0:
        return float("inf")
    return 20 * np.log10(max_val / np.sqrt(mse_val))
