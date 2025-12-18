from dataclasses import dataclass
from typing import List, Dict, Any, Iterator
from pathlib import Path


@dataclass
class Config:
    target_dir: Path
    exclude_patterns: List[str]
    pytest_args: List[str]
    timeout_secs: int
    max_mutants: int
    min_score_pct: float
    dry_run: bool


class MutantLocation(Dict[str, Any]):
    lineno: int
    col_offset: int
    mut_id: str
    transformer_cls: type
    new_op: Any = None


class MutantResult(Dict[str, Any]):
    file: Path
    mut_id: str
    killed: bool
    timed_out: bool


class Stats(Dict[str, int]):
    total: int = 0
    killed: int = 0
    survived: int = 0
    timedout: int = 0