import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.compute as pc
from pyarrow import Type
from collections import Counter, defaultdict
from typing import Dict, List, Optional
from tqdm import tqdm
import math

from .types import ColumnStats

class StatsAccumulator:
    def __init__(self, sample_limit: int = 1000):
        self.sample_limit = sample_limit
        self.samples = []

    def add_samples(self, array: pa.Array):
        valid = array.drop_null()
        new_samples = valid.to_pylist()[:self.sample_limit - len(self.samples)]
        self.samples.extend(new_samples)
        if len(self.samples) > self.sample_limit:
            self.samples = self.samples[:self.sample_limit]

    def get_distinct_approx(self) -> Optional[int]:
        if not self.samples:
            return None
        return len(set(self.samples))

    def get_top_values(self, n: int = 5) -> Optional[Dict[str, float]]:
        if not self.samples:
            return None
        counter = Counter(self.samples)
        total = len(self.samples)
        return {k: round(v / total * 100, 1) for k, v in counter.most_common(n)}

class NumericAccumulator(StatsAccumulator):
    def __init__(self, sample_limit: int = 1000):
        super().__init__(sample_limit)
        self.sum_val = 0.0
        self.sum_sq = 0.0
        self.min_val = None
        self.max_val = None
        self.count = 0
        self.nulls = 0

    def update(self, array: pa.Array):
        mask_sum = (~array.is_null()).sum().as_py()
        self.nulls += len(array) - mask_sum
        if mask_sum > 0:
            self.count += mask_sum
            minv = pc.min(array).as_py()
            maxv = pc.max(array).as_py()
            sumv = pc.sum(array).as_py()
            self.sum_val += sumv
            sq = pc.sum(pc.square(array)).as_py()
            self.sum_sq += sq
            if self.min_val is None or minv < self.min_val:
                self.min_val = minv
            if self.max_val is None or maxv > self.max_val:
                self.max_val = maxv
        self.add_samples(array)

    def finalize(self):
        mean = self.sum_val / self.count if self.count > 0 else None
        return {
            "min": self.min_val,
            "max": self.max_val,
            "mean": mean,
        }

class StringAccumulator(StatsAccumulator):
    def update(self, array: pa.Array):
        self.add_samples(array)

    def finalize(self):
        return {}

def compute_stats(dataset: ds.Dataset, column_name: str, sample_limit: int) -> ColumnStats:
    col = dataset.schema.field(column_name)
    pa_type = str(col.type)
    logical_type = col.type.to_string() if hasattr(col.type, 'to_string') else pa_type

    acc = None
    total_rows = 0
    nulls_total = 0

    scanner = dataset.scanner(columns=[column_name], batch_size=65536)
    pbar = tqdm(total=scanner.estimated_num_rows or 0, desc=f"Scanning {column_name}", unit="rows")

    for batch in scanner.to_batches():
        total_rows += batch.num_rows
        array = batch.column(column_name)
        null_cnt = array.null_count
        nulls_total += null_cnt
        if acc is None:
            if pa.types.is_floating(array.type) or pa.types.is_integer(array.type):
                acc = NumericAccumulator(sample_limit)
            else:
                acc = StringAccumulator(sample_limit)
        acc.update(array)
        pbar.update(batch.num_rows)
    pbar.close()

    null_pct = (nulls_total / total_rows * 100) if total_rows > 0 else 0
    count = total_rows - nulls_total

    finalize = acc.finalize()
    top = acc.get_top_values() if isinstance(acc, StringAccumulator) else None
    distinct = acc.get_distinct_approx()

    alerts = []
    if null_pct > 10:
        alerts.append("High null ratio")
    if distinct and distinct > 10000:
        alerts.append("High cardinality")

    hist = _ascii_histogram(acc.samples) if acc.samples else None

    return ColumnStats(
        name=column_name,
        pa_type=pa_type,
        logical_type=logical_type,
        count=count,
        null_count=nulls_total,
        null_pct=null_pct,
        min_val=finalize.get("min"),
        max_val=finalize.get("max"),
        mean=finalize.get("mean"),
        distinct_approx=distinct,
        top_values=top,
        histogram_ascii=hist,
        quality_alerts=alerts,
    )

def _ascii_histogram(values: List[float], width: int = 50, bins: int = 20) -> str:
    if not values:
        return ""
    minv = min(values)
    maxv = max(values)
    if minv == maxv:
        return "█" * width
    hist = [0] * bins
    for v in values:
        idx = min(bins - 1, math.floor((v - minv) / (maxv - minv) * (bins - 1)))
        hist[idx] += 1
    maxh = max(hist)
    bars = []
    for h in hist:
        bar_len = int((h / maxh) * width) if maxh > 0 else 0
        bars.append("█" * bar_len + "░" * (width - bar_len))
    return "\n".join(bars)
