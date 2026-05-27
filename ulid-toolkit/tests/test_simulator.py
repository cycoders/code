from ulid_toolkit.simulator import estimate_collision

def test_collision_probability_bounds():
    p = estimate_collision(4, 1000, 100)
    assert 0 <= p <= 1

def test_zero_nodes_zero_prob():
    assert estimate_collision(0, 10, 1) == 0.0