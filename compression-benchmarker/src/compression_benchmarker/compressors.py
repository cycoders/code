import bz2
import gzip
import io
import lzma
import brotli
import lz4.frame
import zstandard as zstd_

from typing import Protocol


class Compressor(Protocol):
    def compress(self, data: bytes) -> bytes: ...
    def decompress(self, data: bytes) -> bytes: ...


class GzipCompressor:
    def __init__(self, level: int = 6):
        self.level = max(1, min(9, level))

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)


class Bz2Compressor:
    def __init__(self, level: int = 6):
        self.level = max(1, min(9, level))

    def compress(self, data: bytes) -> bytes:
        return bz2.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return bz2.decompress(data)


class LzmaCompressor:
    def __init__(self, level: int = 6):
        self.level = max(0, min(9, level))

    def compress(self, data: bytes) -> bytes:
        return lzma.compress(data, preset=self.level)

    def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)


class BrotliCompressor:
    def __init__(self, level: int = 6):
        self.quality = max(0, min(11, level))

    def compress(self, data: bytes) -> bytes:
        return brotli.compress(data, quality=self.quality)

    def decompress(self, data: bytes) -> bytes:
        return brotli.decompress(data)


class ZstdCompressor:
    def __init__(self, level: int = 3):
        self.level = max(-131072, min(22, level))  # zstd range
        self._cctx = zstd_.ZstdCompressor(level=self.level)

    def compress(self, data: bytes) -> bytes:
        return self._cctx.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return zstd_.ZstdDecompressor().decompress(data)


class Lz4Compressor:
    def __init__(self, level: int = 0):
        self.level = max(0, min(12, level))

    def compress(self, data: bytes) -> bytes:
        return lz4.frame.compress(data, compression_level=self.level)

    def decompress(self, data: bytes) -> bytes:
        return lz4.frame.decompress(data)


def get_compressor(algo: str, level: int) -> Compressor:
    algo = algo.lower()
    if algo == "gzip":
        return GzipCompressor(level)
    elif algo == "bz2":
        return Bz2Compressor(level)
    elif algo == "lzma":
        return LzmaCompressor(level)
    elif algo == "brotli":
        return BrotliCompressor(level)
    elif algo == "zstd":
        return ZstdCompressor(level)
    elif algo == "lz4":
        return Lz4Compressor(level)
    else:
        raise ValueError(f"Unknown compressor: {algo}")
