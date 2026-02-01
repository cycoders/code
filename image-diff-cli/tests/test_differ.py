import pytest
from image_diff_cli.differ import compute_similarity, SimilarityResult


@pytest.mark.parametrize("resize", ["none", "fit", "crop"])
def test_compute_similarity(solid_red, solid_green, resize, tmp_path):
    # Save to files
    red_path = tmp_path / "red.png"
    green_path = tmp_path / "green.png"
    Image.fromarray(solid_red).save(red_path)
    Image.fromarray(solid_green).save(green_path)

    result = compute_similarity(str(red_path), str(green_path), resize)
    assert isinstance(result, SimilarityResult)
    assert result.ssim < 1.0
    assert result.psnr < 100


@pytest.mark.parametrize("mode", ["fit", "crop"])
def test_resize(mode):
    from image_diff_cli.image_utils import resize_images
    import numpy as np

    img1 = np.zeros((10, 10, 3), np.uint8)
    img2 = np.ones((20, 5, 3), np.uint8)

    r1, r2 = resize_images(img1, img2, mode)
    assert r1.shape == r2.shape
    assert r1.shape[0] > 0
