import numpy as np
import pytest
from PIL import Image

@pytest.fixture
def solid_red():
    """255,0,0 image 10x10."""
    img = Image.new("RGB", (10, 10), (255, 0, 0))
    return np.array(img)

@pytest.fixture
def solid_green():
    img = Image.new("RGB", (10, 10), (0, 255, 0))
    return np.array(img)

@pytest.fixture
def noisy_red():
    """Red + noise."""
    img = Image.new("RGB", (10, 10), (255, 0, 0))
    arr = np.array(img)
    arr += np.random.randint(-10, 10, arr.shape)
    return np.clip(arr, 0, 255).astype(np.uint8)
