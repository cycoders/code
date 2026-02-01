import numpy as np
import pytest
from image_diff_cli.metrics import ssim, psnr, mse


def test_ssim_identical(solid_red):
    assert ssim(solid_red, solid_red) == 1.0


def test_ssim_different(solid_red, solid_green):
    score = ssim(solid_red, solid_green)
    assert 0 < score < 1


def test_mse(solid_red, solid_green):
    m = mse(solid_red, solid_green)
    assert m > 40000  # Rough


def test_psnr(solid_red, solid_green):
    p = psnr(solid_red, solid_green)
    assert p < 50


def test_psnr_identical(solid_red):
    assert np.isinf(psnr(solid_red, solid_red))


@pytest.mark.parametrize("metric", [ssim, mse, psnr])
def test_channel_avg(solid_red, noisy_red, metric):
    # Grayscale avg
    score = metric(solid_red, noisy_red)
    assert score is not None
