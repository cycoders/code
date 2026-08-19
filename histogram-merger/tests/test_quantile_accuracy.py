from histogram_merger.ddsketch import DDSketch


def test_high_percentile():
    sk = DDSketch()
    for i in range(10000):
        sk.add(i)
    assert 9800 < sk.quantile(0.99) < 10200