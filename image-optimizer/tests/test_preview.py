from PIL import Image
from image_optimizer.preview import image_to_ascii, side_by_side_ascii


def test_image_to_ascii():
    img = Image.new("RGB", (20, 10), color=(128, 128, 128))
    ascii_art = image_to_ascii(img, width=40, height=20)
    lines = ascii_art.splitlines()
    assert len(lines) == 20
    assert len(lines[0]) == 40
    assert "-" in ascii_art  # Mid gray


def test_side_by_side_ascii():
    left = "###\n###"
    right = "...\n..."
    combined = side_by_side_ascii(left, right, char_width=3)
    assert "### | ..." in combined
    assert len(combined.splitlines()) == 2