import pytest
from PIL import Image

import numpy as np
from image_diff_cli.image_utils import load_image, resize_images


def test_load_image(tmp_path):
    img = Image.new("RGB", (100, 100), "red")
    path = tmp_path / "test.png"
    img.save(path)

    arr = load_image(str(path))
    assert arr.shape == (100, 100, 3)
    assert np.all(arr[:, :, 0] == 255)


def test_load_max_size(tmp_path):
    large = Image.new("RGB", (3000, 3000))
    path = tmp_path / "large.png"
    large.save(path)

    small = load_image(str(path), max_size=100)
    assert small.shape[0] <= 100
