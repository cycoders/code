LOCK_COSTS = {'postgres': 1.8, 'mysql': 2.3, 'sqlite': 0.1}

def lock_cost(dialect):
    return LOCK_COSTS.get(dialect, 1.0)