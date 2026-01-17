import sys
import json
import jmespath
import random
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Tuple, Any, Dict
from tqdm import tqdm
from rich.console import Console
from rich.table import Table

console = Console()

def stream_dicts(input_file: Optional[str], strict: bool = False) -> Iterator[Tuple[Dict[str, Any], int]]:
    """Yield (data, line_num) from JSONL source. Skips empty/malformed if not strict."""
    def _read_lines():
        ln = 0
        if input_file:
            with open(input_file, encoding="utf-8") as f:
                for ln, line in enumerate(f, 1):
                    yield line.rstrip("\n"), ln
        else:
            for ln, line in enumerate(sys.stdin, 1):
                yield line.rstrip("\n"), ln

    for line, ln in _read_lines():
        if not line.strip():
            continue
        try:
            yield json.loads(line), ln
        except json.JSONDecodeError:
            if strict:
                raise ValueError(f"Invalid JSON on line {ln}")
            console.print(f"[yellow]Skip malformed line {ln}[/]")

@contextmanager
def output_writer(out_file: Optional[str]):
    """Context for JSONL writer."""
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            yield f
    else:
        yield sys.stdout

def _print_summary(mode: str, processed: int, outputted: Optional[int] = None):
    table = Table(title=f"{mode} Summary", box=None, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Processed lines", str(processed))
    if outputted is not None:
        table.add_row("Output lines", str(outputted))
    console.print(table)

def run_filter(
    input_file: Optional[str],
    output_file: Optional[str],
    field_expr: str,
    op: str,
    value: Any,
    strict: bool,
    verbose: bool,
):
    pbar = tqdm(desc="Filter", unit="lines", disable=not verbose)
    processed, outputted = 0, 0
    with output_writer(output_file) as writer:
        for data, _ in stream_dicts(input_file, strict):
            processed += 1
            pbar.update()
            try:
                val = jmespath.search(field_expr, data)
                if apply_op(val, op, value):
                    writer.write(json.dumps(data, separators=(',', ':')) + "\n")
                    outputted += 1
            except jmespath.JMESPathError:
                if strict:
                    raise
    pbar.close()
    _print_summary("Filter", processed, outputted)

def run_transform(input_file: Optional[str], output_file: Optional[str], expr: str, strict: bool, verbose: bool):
    pbar = tqdm(desc="Transform", unit="lines", disable=not verbose)
    processed, outputted = 0, 0
    with output_writer(output_file) as writer:
        for data, _ in stream_dicts(input_file, strict):
            processed += 1
            pbar.update()
            try:
                new_data = jmespath.search(expr, data)
                writer.write(json.dumps(new_data, separators=(',', ':')) + "\n")
                outputted += 1
            except jmespath.JMESPathError:
                if strict:
                    raise
    pbar.close()
    _print_summary("Transform", processed, outputted)

def run_sample(input_file: Optional[str], output_file: Optional[str], fraction: float, strict: bool, verbose: bool):
    pbar = tqdm(desc="Sample", unit="lines", disable=not verbose)
    processed, outputted = 0, 0
    with output_writer(output_file) as writer:
        for data, _ in stream_dicts(input_file, strict):
            processed += 1
            pbar.update()
            if random.random() < fraction:
                writer.write(json.dumps(data, separators=(',', ':')) + "\n")
                outputted += 1
    pbar.close()
    _print_summary("Sample", processed, outputted)

def parse_metrics(metrics_str: str) -> list[tuple[str, Optional[str]]]:
    res = []
    for part in [p.strip() for p in metrics_str.split(",") if p.strip()]:
        if ":" in part:
            agg, fld = part.split(":", 1)
            res.append((agg.lower(), fld))
        else:
            res.append((part.lower(), None))
    return res

def run_aggregate(
    input_file: Optional[str],
    output_file: Optional[str],
    group_by: str,
    metrics_str: str,
    strict: bool,
    verbose: bool,
):
    parsed_metrics = parse_metrics(metrics_str)
    pbar = tqdm(desc="Aggregate", unit="lines", disable=not verbose)
    processed = 0
    groups: Dict[Any, Dict[str, Any]] = defaultdict(dict)
    for data, _ in stream_dicts(input_file, strict):
        processed += 1
        pbar.update()
        try:
            key = jmespath.search(group_by, data)
            if key is None:
                continue
            group = groups[key]
            group["_count"] = group.get("_count", 0) + 1
            for agg, fld in parsed_metrics:
                if fld is None:
                    continue
                val = jmespath.search(fld, data)
                if not isinstance(val, (int, float)):
                    continue
                if agg in ("sum", "avg"):
                    sk = f"sum_{fld}"
                    group[sk] = group.get(sk, 0.0) + val
                elif agg == "min":
                    mk = f"min_{fld}"
                    group[mk] = min(group.get(mk, float("inf")), val)
                elif agg == "max":
                    mk = f"max_{fld}"
                    group[mk] = max(group.get(mk, float("-inf")), val)
        except jmespath.JMESPathError:
            if strict:
                raise
    pbar.close()
    outputted = 0
    with output_writer(output_file) as writer:
        for key, group in groups.items():
            res: Dict[str, Any] = {"group": key, "count": group["_count"]}
            for agg, fld in parsed_metrics:
                if fld is None:
                    continue
                if agg == "sum":
                    res[f"{agg}_{fld}"] = group.get(f"sum_{fld}", 0.0)
                elif agg == "avg":
                    cnt = group["_count"]
                    res[f"{agg}_{fld}"] = group.get(f"sum_{fld}", 0.0) / cnt if cnt else 0.0
                elif agg in ("min", "max"):
                    res[f"{agg}_{fld}"] = group.get(f"{agg}_{fld}", None)
            writer.write(json.dumps(res, separators=(',', ':')) + "\n")
            outputted += 1
    _print_summary("Aggregate", processed, outputted)

def run_stats(input_file: Optional[str], metrics_str: str, strict: bool, verbose: bool):
    parsed_metrics = parse_metrics(metrics_str)
    pbar = tqdm(desc="Stats", unit="lines", disable=not verbose)
    processed = 0
    stats: Dict[str, Any] = {"_count": 0}
    uniques: Dict[str, set] = {}
    for data, _ in stream_dicts(input_file, strict):
        processed += 1
        pbar.update()
        stats["_count"] += 1
        for agg, fld in parsed_metrics:
            if agg == "unique" and fld:
                uniques.setdefault(fld, set()).add(json.dumps(jmespath.search(fld, data)))
            # Global sum/min/max similar to aggregate but single group
            try:
                val = jmespath.search(fld, data)
                if isinstance(val, (int, float)):
                    if agg in ("sum", "avg"):
                        sk = f"sum_{fld}"
                        stats[sk] = stats.get(sk, 0.0) + val
                    elif agg == "min":
                        mk = f"min_{fld}"
                        stats[mk] = min(stats.get(mk, float("inf")), val)
                    elif agg == "max":
                        mk = f"max_{fld}"
                        stats[mk] = max(stats.get(mk, float("-inf")), val)
            except jmespath.JMESPathError:
                pass
    pbar.close()
    # Compute
    table = Table(title="Stats", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")
    table.add_row("Processed", str(processed))
    table.add_row("Count", str(stats["_count"]))
    for agg, fld in parsed_metrics:
        if fld is None:
            continue
        if agg == "unique":
            table.add_row(f"Unique {fld}", str(len(uniques.get(fld, set()))))
        elif agg == "sum":
            table.add_row(f"Sum {fld}", f"{stats.get(f'sum_{fld}', 0):,.2f}")
        elif agg == "avg":
            avg = stats.get(f"sum_{fld}", 0.0) / stats["_count"] if stats["_count"] else 0
            table.add_row(f"Avg {fld}", f"{avg:.2f}")
        elif agg in ("min", "max"):
            table.add_row(f"{agg.capitalize()} {fld}", str(stats.get(f"{agg}_{fld}", "N/A")))
    console.print(table)

# Alias for utils
from .utils import apply_op, parse_value