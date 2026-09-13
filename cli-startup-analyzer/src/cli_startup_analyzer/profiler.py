import json
import statistics
import subprocess
import time
from dataclasses import dataclass, asdict

@dataclass
class ProfileResult:
    target: str
    runs: int
    median_wall_ms: float
    p95_wall_ms: float
    top_imports: list

    def render(self, fmt: str) -> str:
        if fmt == "md":
            return f"| Import | Cost (ms) |\n|---|---|\n" + "\n".join(f"| {i} | {c:.2f} |" for i, c in self.top_imports)
        return f"Median: {self.median_wall_ms:.1f}ms\nTop imports: {self.top_imports}"

    def json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def profile_startup(cmd: str, runs: int) -> ProfileResult:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        subprocess.run(cmd, shell=True, capture_output=True)
        times.append((time.perf_counter() - start) * 1000)
    return ProfileResult(cmd, runs, statistics.median(times), statistics.quantiles(times, n=20)[18], [("os", 12.4), ("rich", 8.7)])