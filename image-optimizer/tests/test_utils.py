import pytest
from image_optimizer.utils import get_image_files


def test_get_image_files_single(tmp_image_png):
    files = get_image_files(str(tmp_image_png))
    assert len(files) == 1
    assert files[0].name == "test.png"


def test_get_image_files_dir(tmp_path, tmp_image_png, tmp_image_jpg):
    dir_path = tmp_path / "images"
    dir_path.mkdir()
    tmp_image_png.rename(dir_path / "a.png")
    tmp_image_jpg.rename(dir_path / "b.jpg")

    files = get_image_files(str(dir_path), recursive=False)
    assert len(files) == 2


def test_recursive(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "sub").mkdir()
    (root / "sub" / "img.png").touch()
    (root / "img.jpg").touch()

    files = get_image_files(str(root), recursive=True)
    assert len(files) == 2


def test_no_images(tmp_path):
    files = get_image_files(str(tmp_path))
    assert len(files) == 0