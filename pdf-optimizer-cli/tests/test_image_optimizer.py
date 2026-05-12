import io

import pytest
from PIL import Image

from pdf_optimizer_cli.image_optimizer import optimize_image


@pytest.fixture
def sample_jpeg():
    img = Image.new('RGB', (100, 100), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=95)
    return buf.getvalue()


@pytest.fixture
def sample_png():
    img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()


def test_optimize_jpeg_reduces_size(sample_jpeg):
    data = sample_jpeg
    opt_data, improved = optimize_image(data, quality=70)
    assert improved
    assert len(opt_data) < len(data)


def test_optimize_png_converts(sample_png):
    data = sample_png
    opt_data, improved = optimize_image(data, quality=85)
    assert improved  # PNG larger, converts to JPEG
    assert b'JFIF' in opt_data  # JPEG marker


def test_no_change_if_no_improvement(sample_jpeg):
    data = sample_jpeg
    # High quality, low reduction
    opt_data, improved = optimize_image(data, quality=95)
    assert not improved or len(opt_data) >= len(data) * 0.95


def test_handles_invalid_image():
    invalid_data = b'GARBAGE'
    opt_data, improved = optimize_image(invalid_data)
    assert not improved
    assert opt_data == invalid_data


def test_empty_data():
    opt_data, improved = optimize_image(b'')
    assert not improved
    assert opt_data == b''
