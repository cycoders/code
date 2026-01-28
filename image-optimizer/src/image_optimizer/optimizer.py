from __future__ import annotations
import os
from typing import Dict, Any
from io import BytesIO

from PIL import Image

SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "webp", "avif", "tiff", "tif"}


def optimize_image(
    img_path: str, target_format: str = "auto", quality: int = 85
) -> Dict[str, Any]:
    """Optimize a single image and return metadata + optimized bytes."""
    
    if not os.path.isfile(img_path):
        raise ValueError(f"Not a file: {img_path}")

    original_size = os.path.getsize(img_path)
    if original_size == 0:
        raise ValueError("Empty file")

    with Image.open(img_path) as img:
        # Validate image
        img.verify()
        img = Image.open(img_path)  # Reopen after verify

        # Auto format
        if target_format == "auto":
            target_format = "webp" if img.mode in ("RGB", "RGBA") else "png"

        buf = BytesIO()
        save_kwargs: Dict[str, Any] = {"quality": quality, "optimize": True}

        try:
            if target_format == "webp":
                save_kwargs["method"] = 6  # Best compression
                img.save(buf, format="WEBP", **save_kwargs)
            elif target_format == "avif":
                save_kwargs["method"] = 6
                img = img.convert("RGB")  # AVIF primary support
                img.save(buf, format="AVIF", **save_kwargs)
            elif target_format == "jpg":
                img = img.convert("RGB")
                save_kwargs["progressive"] = True
                img.save(buf, format="JPEG", **save_kwargs)
            elif target_format == "png":
                img.save(buf, format="PNG", optimize=True, **save_kwargs)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")
        except Exception as e:
            raise RuntimeError(f"Failed to save as {target_format}: {e}")

        optimized_bytes = buf.getvalue()
        optimized_size = len(optimized_bytes)
        savings_percent = max(0, (1 - optimized_size / original_size) * 100)

        return {
            "input": img_path,
            "original_size": original_size,
            "output_size": optimized_size,
            "savings_percent": savings_percent,
            "format": target_format,
            "optimized_image": optimized_bytes,
        }