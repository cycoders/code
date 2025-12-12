import time
import psutil
from typing import List, Dict, Any
from .utils import value_to_braille


class ProcessMonitor:
    """Monitors processes with accurate CPU delta sampling."""

    def __init__(self, num_cores: int | None = None) -> None:
        self.num_cores = num_cores or psutil.cpu_count(logical=False)
        self._proc_times: Dict[int, tuple[float, float]] = {}
        self._last_sample_time: float = 0.0

    def sample(self, cpu_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Sample processes, compute CPU%, filter/sort by CPU+Mem."""
        now = time.time()
        delta_time = now - self._last_sample_time
        if delta_time <= 0:
            self._last_sample_time = now
            return []

        procs: List[Dict[str, Any]] = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_times', 'memory_percent']):
            try:
                info = p.info
                pid: int = info['pid']
                ctimes = info['cpu_times']
                prev_utime, prev_stime = self._proc_times.get(pid, (0.0, 0.0))
                delta_user = ctimes.utime - prev_utime
                delta_sys = ctimes.stime - prev_stime
                cpu_pct = ((delta_user + delta_sys) / delta_time / self.num_cores) * 100
                if cpu_pct < cpu_threshold:
                    continue
                info = {
                    'pid': pid,
                    'name': info['name'][:24].ljust(24),
                    'cpu_percent': max(0.0, cpu_pct),
                    'mem_percent': info['memory_percent'],
                }
                self._proc_times[pid] = (ctimes.utime, ctimes.stime)
                procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                if pid in self._proc_times:
                    del self._proc_times[pid]
                continue

        # Cleanup stale PIDs
        active_pids = {p['pid'] for p in procs}
        self._proc_times = {pid: t for pid, t in self._proc_times.items() if pid in active_pids}

        procs.sort(key=lambda p: p['cpu_percent'] + p['mem_percent'], reverse=True)
        self._last_sample_time = now
        return procs

    def get_system_stats(self) -> Dict[str, float]:
        """Get aggregate system CPU/memory stats."""
        vm = psutil.virtual_memory()
        return {
            'cpu_percent': psutil.cpu_percent(interval=None),
            'mem_percent': vm.percent,
            'mem_used_gb': round(vm.used / (1024 ** 3), 1),
            'mem_total_gb': round(vm.total / (1024 ** 3), 1),
        }