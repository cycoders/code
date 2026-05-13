import random
import time
from typing import Dict, Any, List

from .config import Config
from .backend import Backend
from .strategies import SELECTORS


def compute_percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * p / 100)
    return sorted_data[min(idx, len(sorted_data) - 1)]


def run_simulation(cfg: Config) -> Dict[str, Any]:
    if cfg.seed is not None:
        random.seed(cfg.seed)

    backends: List[Backend] = [Backend(bcfg) for bcfg in cfg.backends]

    selector_cls = SELECTORS[cfg.strategy]
    selector = selector_cls(backends) if cfg.strategy == "weighted-rr" else selector_cls()

    stats = {
        'global': {'resp_times': [], 'errors': 0, 'total_reqs': 0},
        'backends': {b.name: b.stats for b in backends},
        'live_data': []  # for live render
    }

    current_time = 0.0
    total_steps = int(cfg.duration / cfg.dt)

    req_counter = 0
    processed_reqs = 0

    for step in range(total_steps):
        current_time += cfg.dt

        # Poisson arrivals
        arrivals = random.poisson(cfg.arrival_rate * cfg.dt)
        for _ in range(arrivals):
            client_ip = f"192.168.1.{random.randint(1, 254)}"
            backend = selector.select(backends, client_ip)
            if backend:
                backend.enqueue(f"req_{req_counter}", current_time)
                stats['global']['total_reqs'] += 1
                req_counter += 1

        # Tick backends
        for backend in backends:
            completed = backend.tick(current_time)
            for comp in completed:
                stats['global']['resp_times'].append(comp['resp_time'])
                if not comp['success']:
                    stats['global']['errors'] += 1
                processed_reqs += 1

        # Live snapshot every 1s
        if int(current_time) % 1 == 0:
            stats['live_data'].append({
                'time': current_time,
                'processed': processed_reqs,
                'qlens': {b.name: len(b.queue) for b in backends},
                'actives': {b.name: len(b.active) for b in backends},
                'util': {b.name: b.utilization() for b in backends}
            })

    # Final stats
    global_stats = stats['global']
    global_stats.update({
        'p50': compute_percentile(global_stats['resp_times'], 50),
        'p95': compute_percentile(global_stats['resp_times'], 95),
        'p99': compute_percentile(global_stats['resp_times'], 99),
        'error_rate': global_stats['errors'] / max(1, global_stats['total_reqs']),
        'throughput': global_stats['total_reqs'] / cfg.duration,
    })

    for b in backends:
        bstats = stats['backends'][b.name]
        if bstats['resp_times']:
            bstats.update({
                'p95': compute_percentile(bstats['resp_times'], 95),
                'avg_resp': sum(bstats['resp_times']) / len(bstats['resp_times']),
                'avg_util': bstats.get('avg_util', 0),
            })

    return stats
