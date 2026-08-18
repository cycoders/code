import numpy as np

class DiscreteEventSimulator:
    def __init__(self, config):
        self.config = config
    def run(self, pool_size):
        # placeholder high-fidelity simulation
        return {"p95": 95.0 + np.random.randn() * 5, "throughput": pool_size * 120}