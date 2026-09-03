from typing import List

class RelationGraph:
    """Topological sort for FK dependencies."""
    def __init__(self):
        self.edges = []

    def add_fk(self, parent: str, child: str):
        self.edges.append((parent, child))