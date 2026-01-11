import os
from pathlib import Path
from typing import Generator, Dict, Any, List


def get_file_sizes(file1: Path, file2: Path) -> tuple[int, int]:
    """Get file sizes with error handling."""
    try:
        return os.path.getsize(file1), os.path.getsize(file2)
    except OSError as e:
        raise typer.Exit(f"Error reading sizes: {e}") from e


def bytes_to_hex_ascii(data: bytes) -> tuple[str, str]:
    """Convert bytes to hex dump string and ASCII representation."""
    hex_bytes = " ".join(f"{b:02x}" for b in data)
    ascii_repr = "".join(chr(b) if 32 <= b <= 126 else "." for b in data)
    return hex_bytes, ascii_repr


def compare_paths(
    path1: Path, path2: Path, block_size: int = 16
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator for comparable blocks.

    Yields dicts with offset, hex/ascii for both, diff_positions (list of changed byte indices).
    """
    size1 = os.path.getsize(path1)
    size2 = os.path.getsize(path2)
    min_size = min(size1, size2)

    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        offset = 0
        f1_pos = 0
        f2_pos = 0
        while offset < min_size:
            remaining1 = size1 - f1_pos
            remaining2 = size2 - f2_pos
            bs = min(block_size, remaining1, remaining2)
            if bs == 0:
                break

            chunk1 = f1.read(bs)
            chunk2 = f2.read(bs)
            assert len(chunk1) == bs == len(chunk2)

            diffs = [i for i, (b1, b2) in enumerate(zip(chunk1, chunk2)) if b1 != b2]
            hex1, ascii1 = bytes_to_hex_ascii(chunk1)
            hex2, ascii2 = bytes_to_hex_ascii(chunk2)

            yield {
                "offset": offset,
                "hex1": hex1,
                "ascii1": ascii1,
                "hex2": hex2,
                "ascii2": ascii2,
                "diff_positions": diffs,
                "changes": len(diffs),
            }

            offset += bs
            f1_pos += bs
            f2_pos += bs