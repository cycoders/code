from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class ElementCoverage:
    total: int = 0
    typed: int = 0

    @property
    def percentage(self) -> float:
        return (self.typed / self.total * 100) if self.total else 100.0

    def merge(self, other: "ElementCoverage") -> None:
        self.total += other.total
        self.typed += other.typed

@dataclass
class FileStats:
    path: str
    funcs: ElementCoverage = field(default_factory=ElementCoverage)
    params: ElementCoverage = field(default_factory=ElementCoverage)
    returns: ElementCoverage = field(default_factory=ElementCoverage)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "funcs": asdict(self.funcs),
            "params": asdict(self.params),
            "returns": asdict(self.returns),
        }

@dataclass
class OverallStats:
    files: int = 0
    funcs: ElementCoverage = field(default_factory=ElementCoverage)
    params: ElementCoverage = field(default_factory=ElementCoverage)
    returns: ElementCoverage = field(default_factory=ElementCoverage)
    file_stats: List[FileStats] = field(default_factory=list)

    def func_coverage(self) -> float:
        return self.funcs.percentage

    def param_coverage(self) -> float:
        return self.params.percentage

    def return_coverage(self) -> float:
        return self.returns.percentage

    def merge(self, file_stats: FileStats) -> None:
        self.files += 1
        self.funcs.merge(file_stats.funcs)
        self.params.merge(file_stats.params)
        self.returns.merge(file_stats.returns)
        self.file_stats.append(file_stats)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": {
                "files": self.files,
                "funcs": asdict(self.funcs),
                "params": asdict(self.params),
                "returns": asdict(self.returns),
            },
            "files": [fs.to_dict() for fs in self.file_stats],
        }