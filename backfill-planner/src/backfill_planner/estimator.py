from typing import Tuple
from math import ceil

from .config import BackfillConfig


def optimal_batch_size(config: BackfillConfig) -> int:
    """
    Compute optimal batch size balancing throughput, memory, and time.

    batch_size = min(
        throughput_avg * max_batch_seconds,
        max_memory_mb * 1024**2 / row_size_bytes,
        1e6  # sane upper limit
    )
    """
    throughput_limit = config.write_throughput_avg * config.max_batch_seconds
    memory_limit = (config.max_memory_mb * 1024**2) // config.row_size_bytes
    upper_limit = 1_000_000
    return int(min(throughput_limit, memory_limit, upper_limit))


def estimate_phase_time(rows: int, throughput_avg: float, safety_factor: float = 1.2) -> float:
    """Est. time in seconds, with safety buffer."""
    return ceil(rows / throughput_avg * safety_factor)


def num_batches(total_rows: int, batch_size: int) -> int:
    return ceil(total_rows / batch_size)


def total_time_estimate(config: BackfillConfig) -> Tuple[float, float]:
    batch_size = optimal_batch_size(config)
    main_phase_rows = config.total_rows
    main_time_sec = estimate_phase_time(main_phase_rows, config.write_throughput_avg)
    overhead = 0.05 * main_time_sec  # 5% for checks
    total_sec = main_time_sec + overhead
    return total_sec, batch_size
