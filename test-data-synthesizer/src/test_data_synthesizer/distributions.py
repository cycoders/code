import numpy as np

class DistributionSampler:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def sample(self, col, n):
        return self.rng.normal(size=n)