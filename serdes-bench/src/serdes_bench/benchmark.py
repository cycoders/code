import statistics
import time
from dataclasses import dataclass
from typing import Any

from .formats import Serializer


@dataclass
class Result:
    format_name: str
    size_bytes: int
    size_kb: float
    ser_time_ms: float
    deser_time_ms: float
    total_time_ms: float
    throughput_ops_s: float
    fidelity: bool
    ser_stdev_ms: float


def measure(
    serializer: Serializer,
    data: Any,
    iters: int,
    warmup: int = 10,
) -> Result:
    """Run ser/de benchmark. Returns avg metrics."""

    # Warmup (JIT, caches)
    for _ in range(warmup):
        ser_bytes = serializer.serialize(data)
        _ = serializer.deserialize(ser_bytes)

    ser_times_ns: list[int] = []
    deser_times_ns: list[int] = []
    ser_bytes: bytes | None = None
    roundtrip: Any = None

    for _ in range(iters):
        # Serialize
        start = time.perf_counter_ns()
        ser_bytes = serializer.serialize(data)
        ser_times_ns.append(time.perf_counter_ns() - start)

        # Deserialize
        start = time.perf_counter_ns()
        roundtrip = serializer.deserialize(ser_bytes)
        deser_times_ns.append(time.perf_counter_ns() - start)

    if ser_bytes is None:
        raise RuntimeError("No serialization occurred")

    size_bytes = len(ser_bytes)
    avg_ser_ms = statistics.mean(ser_times_ns) / 1_000_000
    avg_deser_ms = statistics.mean(deser_times_ns) / 1_000_000
    total_ms = avg_ser_ms + avg_deser_ms
    total_ns = sum(ser_times_ns) + sum(deser_times_ns)
    throughput = (iters * 1_000_000_000) / total_ns if total_ns else 0
    fidelity = roundtrip == data
    ser_stdev_ms = statistics.stdev(ser_times_ns) / 1_000_000 if iters > 1 else 0.0

    format_name = serializer.__class__.__name__.replace('Serializer', '')

    return Result(
        format_name,
        size_bytes,
        size_bytes / 1024,
        avg_ser_ms,
        avg_deser_ms,
        total_ms,
        throughput,
        fidelity,
        ser_stdev_ms,
    )
