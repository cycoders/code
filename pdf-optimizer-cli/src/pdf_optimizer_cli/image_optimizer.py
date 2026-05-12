import io
import logging
from typing import Tuple

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def optimize_image(data: bytes, quality: int = 85) -> Tuple[bytes, bool]:
    """
    Optimize image bytes to JPEG.

    Returns (optimized_bytes, was_improved).
    """
    orig_size = len(data)
    if orig_size == 0:
        return data, False

    try:
        with Image.open(io.BytesIO(data)) as img:
            # Handle transparency by flattening to white background
            if img.mode in ('RGBA', 'LA', 'P'):
                # Convert palette to RGBA if P
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # Create white BG and paste
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != 'RGB':
                img = ImageOps.grayscale(img).convert('RGB') if img.mode == 'L' else img.convert('RGB')

            # Optimize as JPEG
            buffer = io.BytesIO()
            img.save(
                buffer,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True,
            )
            opt_data = buffer.getvalue()

            # Accept if at least 5% smaller
            if len(opt_data) < orig_size * 0.95:
                logger.debug(f"Image optimized: {orig_size} -> {len(opt_data)} bytes ({(1 - len(opt_data)/orig_size)*100:.1f}%)")
                return opt_data, True
            else:
                logger.debug("No improvement from optimization")
                return data, False
    except Exception as e:
        logger.warning(f"Failed to optimize image: {e}")
        return data, False
