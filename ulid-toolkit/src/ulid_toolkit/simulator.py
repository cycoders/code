import random
from collections import Counter

def estimate_collision(nodes: int, ids_per_node: int, trials: int = 10000) -> float:
    collisions = 0
    for _ in range(trials):
        seen = set()
        for _ in range(nodes * ids_per_node):
            val = random.getrandbits(80)
            if val in seen:
                collisions += 1
                break
            seen.add(val)
    return collisions / trials