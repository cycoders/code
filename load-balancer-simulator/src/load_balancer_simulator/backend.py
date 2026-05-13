from collections import deque, defaultdict
import random
from typing import Dict, List, Any


class Backend:
    def __init__(self, config):
        self.name = config.name
        self.capacity = config.capacity
        self.service_time_mean = config.service_time_mean
        self.service_time_std = config.service_time_std
        self.failure_rate = config.failure_rate
        self.weight = config.weight
        self.reset()

    def reset(self):
        self.queue: deque[tuple[str, float]] = deque()  # (req_id, enqueue_time)
        self.active: Dict[str, Dict[str, float]] = {}  # req_id -> {'end_time', 'arr_time', 'service_time'}
        self.stats = {
            'total_reqs': 0,
            'errors': 0,
            'resp_times': [],
            'max_queue_len': 0,
        }

    def current_load(self) -> int:
        return len(self.queue) + len(self.active)

    def utilization(self) -> float:
        return min(1.0, len(self.active) / self.capacity) if self.capacity > 0 else 0.0

    def enqueue(self, req_id: str, time: float):
        self.queue.append((req_id, time))
        self.stats['total_reqs'] += 1
        self.stats['max_queue_len'] = max(self.stats['max_queue_len'], len(self.queue))

    def tick(self, current_time: float) -> List[Dict[str, Any]]:
        completed = []
        # Finish active reqs
        to_remove = []
        for req_id, data in self.active.items():
            if current_time >= data['end_time']:
                resp_time = current_time - data['arr_time']
                success = data['success']
                self.stats['resp_times'].append(resp_time)
                if not success:
                    self.stats['errors'] += 1
                to_remove.append(req_id)
                completed.append({
                    'backend': self.name,
                    'req_id': req_id,
                    'resp_time': resp_time,
                    'success': success
                })
        for req_id in to_remove:
            del self.active[req_id]
        # Start new if possible
        while self.queue and len(self.active) < self.capacity:
            req_id, arr_time = self.queue.popleft()
            service_time = max(0.001, random.normalvariate(self.service_time_mean, self.service_time_std))
            fail = random.random() < self.failure_rate
            end_time = current_time + service_time
            self.active[req_id] = {
                'end_time': end_time,
                'arr_time': arr_time,
                'service_time': service_time,
                'success': not fail
            }
        return completed