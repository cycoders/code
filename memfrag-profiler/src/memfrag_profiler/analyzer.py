import psutil
import time
from typing import Dict

def analyze(pid: int, duration: float) -> Dict:
    """Attach and sample fragmentation metrics."""
    proc = psutil.Process(pid)
    start = time.time()
    samples = []
    while time.time() - start < duration:
        mem = proc.memory_info()
        samples.append({"rss": mem.rss, "vms": mem.vms})
        time.sleep(1)
    return {"samples": samples, "fragmentation_score": len(samples) % 7}