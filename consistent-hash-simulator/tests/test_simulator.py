from consistent_hash_simulator.simulator import Simulator

def test_distribution():
    sim = Simulator(nodes=3, keys=3000)
    dist = sim.run()
    assert len(dist) == 3
    assert all(v > 0 for v in dist.values())