import pytest
from pathlib import Path
import tempfile
from PIL import Image

@pytest.fixture
def tmp_image_png():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.png"
        img = Image.new("RGB", (200, 100), color="red")
        img.save(path, "PNG")
        yield path

@pytest.fixture
def tmp_image_jpg():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.jpg"
        img = Image.new("RGB", (200, 100), color="blue")
        img.save(path, "JPEG", quality=95)
        yield path