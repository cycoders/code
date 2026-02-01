import numpy as np
from PIL import Image
from skimage.transform import resize
from typing import Literal

ResizeMode = Literal["none", "fit", "crop"]


def load_image(path: str, max_size: int = None) -> np.ndarray:
    """
    Load image as RGB numpy array.

    :param max_size: Optional downscale to fit within square.
    """
    with Image.open(path) as pil_img:
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img_array = np.array(pil_img)

        if max_size:
            pil_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            img_array = np.array(pil_img)

        return img_array


def resize_images(img1: np.ndarray, img2: np.ndarray, mode: ResizeMode) -> tuple[np.ndarray, np.ndarray]:
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    if (h1, w1) == (h2, w2):
        return img1, img2

    if mode == "none":
        raise ValueError(f"Size mismatch: {img1.shape} vs {img2.shape}. Use --resize fit|crop.")

    target_shape = (max(h1, h2), max(w1, w2)) if mode == "crop" else (min(h1, h2), min(w1, w2))

    img1_resized = resize(img1, target_shape + (3,), anti_aliasing=True)
    img2_resized = resize(img2, target_shape + (3,), anti_aliasing=True)

    return np.clip(img1_resized * 255, 0, 255).astype(np.uint8), np.clip(img2_resized * 255, 0, 255).astype(np.uint8)
