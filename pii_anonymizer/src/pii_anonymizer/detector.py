import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from rich.progress import Progress

from .patterns import COMPILED_PATTERNS
from .types import PIIColumnStats


class Detector:
    def __init__(self, threshold: float = 0.05, patterns: Dict[str, 're.Pattern'] = None):
        self.threshold = threshold
        self.patterns = patterns or COMPILED_PATTERNS

    def detect_column_stats(self, df: pd.DataFrame) -> List[PIIColumnStats]:
        stats: List[PIIColumnStats] = []
        total_rows = len(df)

        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning columns...", total=len(df.columns))
            for col in df.columns:
                col_series = df[col].astype(str)
                match_counts = {ptype: pattern.findall(str(cell)) for ptype, pattern in self.patterns.items() for cell in col_series if pattern.search(str(cell))}
                total_matches = sum(len(matches) for matches in match_counts.values())
                pct = total_matches / total_rows if total_rows > 0 else 0
                dominant_type = max(match_counts, key=lambda t: len(match_counts[t]), default=None) if match_counts else None
                if pct >= self.threshold:
                    stats.append(PIIColumnStats(
                        column=col,
                        pii_percentage=pct,
                        match_count=total_matches,
                        dominant_type=dominant_type
                    ))
                progress.advance(task)

        return sorted(stats, key=lambda s: s.pii_percentage, reverse=True)

    def get_pii_mask_and_type(self, series: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Per-cell: bool mask if PII, str type of dominant pattern."""
        series_str = series.astype(str)
        mask = pd.Series(False, index=series.index)
        pii_type = pd.Series('', dtype='object', index=series.index)
        best_length = 0

        for ptype, pattern in self.patterns.items():
            matches = series_str.str.findall(pattern)
            has_match = ~pd.Series([len(m) == 0 for m in matches], index=series.index)
            for idx in has_match[has_match].index:
                if len(matches[idx]) > best_length:
                    best_length = len(matches[idx])
                    pii_type[idx] = ptype
                    mask[idx] = True

        return mask, pii_type
