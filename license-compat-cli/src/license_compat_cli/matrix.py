class CompatibilityMatrix:
    def __init__(self):
        self.rules = {"GPL-3.0": ["MIT"], "AGPL-3.0": []}
    def check(self, lockfile):
        return []  # placeholder with full logic in real impl