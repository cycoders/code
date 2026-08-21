from __future__ import annotations
import mmap
from pathlib import Path
from typing import Any

SIGNATURES: dict[bytes, str] = {}


def identify(path: str | Path, *, recursive: bool = False) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    with p.open("rb") as f:
        data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            for magic, ftype in SIGNATURES.items():
                if data.startswith(magic):
                    return [{"path": str(p), "type": ftype, "confidence": 0.95}]
            return [{"path": str(p), "type": "unknown", "confidence": 0.0}]
        finally:
            data.close()