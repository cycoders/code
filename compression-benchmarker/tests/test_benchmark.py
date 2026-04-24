import pytest

from compression_benchmarker.benchmark import benchmark_compressor
from compression_benchmarker.compressors import get_compressor


@pytest.fixture
def compressor():
    return get_compressor("gzip", 6)


@pytest.fixture
def sample_data():
    return b"hello" * 10000


def test_benchmark_smoke(compressor, sample_data):
    res = benchmark_compressor(compressor, sample_data)
    assert res["size_pct"] > 0
    assert res["comp_mbps"] > 0
    assert res["decomp_mbps"] > 0
    assert all(k in res for k in ["comp_time_ms", "decomp_time_ms", "comp_size"])


def test_empty_data(compressor):
    with pytest.raises(ValueError, match="Empty data"):
        benchmark_compressor(compressor, b"")


def test_single_run(compressor, sample_data):
    res = benchmark_compressor(compressor, sample_data, runs=1)
    assert res["comp_time_ms"] >= 0
