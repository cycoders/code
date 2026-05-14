import pandas as pd
from pathlib import Path
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console


def parse_metrics(
    path: str,
    ts_col: str,
    latency_col: Optional[str],
    status_col: Optional[str],
    error_above: int,
    console: Console,
) -> pd.DataFrame:
    """Parse metrics file into timestamp-indexed DataFrame with metric column."""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"File not found: {path}")

    chunksize = 100_000
    dfs = []

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Parsing data...", total=None)

        if path.suffix.lower() in {'.jsonl', '.ndjson', '.json-lines'}:
            # Line-by-line for large JSONL
            df_chunk = pd.DataFrame()
            line_count = 0
            for line in path.open():
                line_count += 1
                try:
                    row = pd.json_normalize(pd.read_json(line.strip(), typ='series'))
                    df_chunk = pd.concat([df_chunk, row], ignore_index=True)
                    if len(df_chunk) >= chunksize:
                        dfs.append(_process_chunk(df_chunk, ts_col, latency_col, status_col, error_above))
                        progress.update(task, advance=chunksize)
                        df_chunk = pd.DataFrame()
                except (ValueError, pd.errors.JsonDecodeError):
                    continue
            if not df_chunk.empty:
                dfs.append(_process_chunk(df_chunk, ts_col, latency_col, status_col, error_above))
        else:
            # CSV with chunks
            chunks = pd.read_csv(path, chunksize=chunksize, low_memory=False)
            for i, chunk in enumerate(chunks):
                dfs.append(_process_chunk(chunk, ts_col, latency_col, status_col, error_above))
                progress.update(task, advance=chunksize)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    return df.sort_values('timestamp').set_index('timestamp').dropna(subset=['timestamp'])


def _process_chunk(
    chunk: pd.DataFrame,
    ts_col: str,
    latency_col: Optional[str],
    status_col: Optional[str],
    error_above: int,
) -> pd.DataFrame:
    chunk = chunk.copy()
    chunk[ts_col] = pd.to_datetime(chunk[ts_col], errors='coerce')
    chunk = chunk.dropna(subset=[ts_col])
    chunk = chunk.rename(columns={ts_col: 'timestamp'})

    if status_col:
        chunk['is_error'] = (pd.to_numeric(chunk[status_col], errors='coerce') >= error_above).astype(int)
    if latency_col:
        chunk['latency'] = pd.to_numeric(chunk[latency_col], errors='coerce')

    return chunk
