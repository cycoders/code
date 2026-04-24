import pytest

from compression_benchmarker.compressors import get_compressor


@pytest.mark.parametrize("algo", ["gzip", "bz2", "lzma", "brotli", "zstd", "lz4"])
@pytest.mark.parametrize("level", [1, 6, 9])
def test_roundtrip(algo: str, level: int) -> None:
    comp = get_compressor(algo, level)
    data = b"testdata" * 1024 + b"\x00\xFF\x80"  # mixed bytes
    cdata = comp.compress(data)
    assert len(cdata) > 0 and len(cdata) < len(data)
    ddata = comp.decompress(cdata)
    assert ddata == data


def test_unknown_algo() -> None:
    with pytest.raises(ValueError, match="Unknown compressor"):
        get_compressor("foo", 6)
