from test_data_synthesizer.distributions import DistributionSampler

def test_reproducible():
    s1 = DistributionSampler(42).sample(None, 5)
    s2 = DistributionSampler(42).sample(None, 5)
    assert (s1 == s2).all()