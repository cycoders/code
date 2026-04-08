import pytest
from serdes_bench.benchmark import measure
from serdes_bench.formats import OrJSONSerializer


def test_measure_positive_metrics(sample_data: dict):
    ser = OrJSONSerializer()
    result = measure(ser, sample_data, iters=100, warmup=5)

    assert result.size_bytes > 0
    assert result.size_kb > 0
    assert result.ser_time_ms > 0
    assert result.deser_time_ms > 0
    assert result.total_time_ms > 0
    assert result.throughput_ops_s > 0
    assert result.fidelity is True
    assert result.ser_stdev_ms >= 0
