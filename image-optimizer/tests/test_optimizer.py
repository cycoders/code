import pytest
from io import BytesIO
from PIL import Image
from image_optimizer.optimizer import optimize_image


@pytest.mark.parametrize(
    "fmt, expected_format",
    [("webp", "WEBP"), ("avif", "AVIF"), ("jpg", "JPEG"), ("png", "PNG")],
)
def test_optimize_formats(tmp_image_png, fmt, expected_format):
    result = optimize_image(str(tmp_image_png), target_format=fmt, quality=90)
    assert result["format"] == fmt
    opt_img = Image.open(BytesIO(result["optimized_image"]))
    assert opt_img.format == expected_format
    assert result["output_size"] < result["original_size"]
    assert result["savings_percent"] > 0


def test_auto_format(tmp_image_png):
    result = optimize_image(str(tmp_image_png), target_format="auto")
    assert result["format"] == "webp"


def test_invalid_format(tmp_image_png):
    with pytest.raises(ValueError, match="Unsupported"):
        optimize_image(str(tmp_image_png), target_format="bmp")


def test_empty_file(tmp_path):
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"")
    with pytest.raises(ValueError, match="Empty"):
        optimize_image(str(empty))