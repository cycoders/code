import matplotlib
matplotlib.use("Agg")  # Headless

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from typing import Literal

DiffMode = Literal["side-by-side", "heatmap", "overlay"]


def save_visualization(img1: np.ndarray, img2: np.ndarray, diff_norm: np.ndarray, path: str, mode: DiffMode):
    """
    Save annotated diff image.

    :param diff_norm: Normalized diff (0-1).
    """
    plt.rcParams["figure.facecolor"] = "white"
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    ax.axis("off")

    if mode == "side-by-side":
        combined = np.hstack((img1, img2))
        ax.imshow(combined)
        ax.set_title("Side-by-Side", pad=20)

    elif mode == "heatmap":
        im = ax.imshow(diff_norm, cmap="jet", vmin=0, vmax=0.1)
        ax.set_title("Difference Heatmap", pad=20)
        plt.colorbar(im, ax=ax, shrink=0.8)

    elif mode == "overlay":
        overlay = img1.copy()
        overlay[diff_norm > 0.01] = [255, 0, 0]  # Red tint anomalies
        ax.imshow(overlay)
        ax.set_title("Red Overlay (Anomalies)", pad=20)

    plt.tight_layout(pad=0)
    plt.savefig(path, bbox_inches="tight", pad_inches=0, facecolor="white")
    plt.close(fig)


def compute_normalized_diff(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    diff = np.abs(img1.astype(np.float32) - img2.astype(np.float32))
    return np.mean(diff, axis=2) / 255.0  # Grayscale normalized 0-1
