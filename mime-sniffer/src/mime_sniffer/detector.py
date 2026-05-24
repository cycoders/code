from __future__ import annotations

import io
import json
from pathlib import Path
from typing import BinaryIO, Optional

SIGNATURES = [
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"PK\x03\x04", "application/zip"),
    (b"Rar!\x1a\x07\x00", "application/x-rar-compressed"),
]

HEURISTICS = {
    b"{": "application/json",
    b"<": "application/xml",
}

def sniff(data: bytes | BinaryIO | str | Path) -> Optional[str]:
    if isinstance(data, (str, Path)):
        with open(data, "rb") as f:
            return _sniff_stream(f)
    if isinstance(data, (bytes, bytearray)):
        return _sniff_bytes(data)
    return _sniff_stream(data)

def _sniff_bytes(b: bytes) -> Optional[str]:
    for sig, mime in SIGNATURES:
        if b.startswith(sig):
            return mime
    first = b.lstrip()[:1]
    return HEURISTICS.get(first)

def _sniff_stream(stream: BinaryIO) -> Optional[str]:
    header = stream.read(16)
    return _sniff_bytes(header)