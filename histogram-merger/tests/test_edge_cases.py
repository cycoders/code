from histogram_merger.ddsketch import DDSketch


def test_empty():
    sk = DDSketch()
    assert sk.quantile(0.99) == 0.0

def test_single_value():
    sk = DDSketch()
    sk.add(42)
    assert sk.quantile(0.5) == 42.0