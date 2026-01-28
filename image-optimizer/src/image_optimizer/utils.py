from pathlib import Path
from typing import List

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".tiff", ".tif"}


def get_image_files(root_path: str, recursive: bool = False) -> List[Path]:
    """Scan path for supported image files."""
    
    root = Path(root_path)
    if not root.exists():
        return []

    files: List[Path] = []
    if root.is_file():
        if root.suffix.lower() in IMAGE_EXTS:
            files.append(root)
        return files

    # Directory scan
    glob_pattern = "**/*" if recursive else "*"
    for ext in IMAGE_EXTS:
        files.extend(root.glob(glob_pattern + ext.lower()))
        files.extend(root.glob(glob_pattern + ext.upper()))  # Case insensitive

    return sorted(files, key=lambda p: p.stat().st_size, reverse=True)


def ensure_dir(dir_path: Path) -> None:
    """Create directory if missing."""
    dir_path.mkdir(parents=True, exist_ok=True)