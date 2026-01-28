from PIL import Image
from typing import Optional

ASCII_CHARS = "@%#*+=-:. "[::-1]  # Darkest to lightest


def image_to_ascii(
    img: Image.Image, width: int = 80, height: Optional[int] = None
) -> str:
    """Convert PIL image to ASCII art."""
    
    # Grayscale
    img_gray = img.convert("L")

    # Preserve aspect ratio
    orig_w, orig_h = img_gray.size
    if height is None:
        height = int((orig_h / orig_w) * width * 0.55)  # ~2:1 terminal

    # Resize
    img_resized = img_gray.resize((width, height), Image.Resampling.LANCZOS)
    pixels = list(img_resized.getdata())

    # Map to chars
    ascii_pixels = [ASCII_CHARS[pixel // (256 // len(ASCII_CHARS))] for pixel in pixels]

    # Format lines
    ascii_art = "\n".join("".join(ascii_pixels[i : i + width]) for i in range(0, len(ascii_pixels), width))
    return ascii_art


def side_by_side_ascii(
    left_ascii: str, right_ascii: str, char_width: int = 50, separator: str = " | "
) -> str:
    """Render two ASCII arts side-by-side."""
    
    left_lines = left_ascii.split("\n")
    right_lines = right_ascii.split("\n")

    max_lines = max(len(left_lines), len(right_lines))
    left_lines += [" " * char_width] * (max_lines - len(left_lines))
    right_lines += [" " * char_width] * (max_lines - len(right_lines))

    paired_lines = [
        f"{left[:char_width]:<{char_width}}{separator}{right}"
        for left, right in zip(left_lines, right_lines)
    ]
    return "\n".join(paired_lines)