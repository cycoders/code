import os
import pytest
from PIL import Image

from image_diff_cli.renderer import compute_normalized_diff, DiffMode


def test_normalized_diff(solid_red, solid_green, tmp_path):
    diff = compute_normalized_diff(solid_red, solid_green)
    assert diff.shape[:2] == (10, 10)
    assert np.all(diff >= 0) and np.all(diff <= 1)


@pytest.mark.parametrize("mode", DiffMode.__args__)  # Literal iter

def test_save(mode, solid_red, solid_green, tmp_path):
    from image_diff_cli.renderer import save_visualization

    diff_norm = compute_normalized_diff(solid_red, solid_green)
    path = tmp_path / "test.png"

    save_visualization(solid_red, solid_green, diff_norm, str(path), mode)

    assert path.exists()
    assert Image.open(path).size == (1200, 600)  # Approx figsize*dpi
