from histogram_merger.ddsketch import DDSketch


def test_add_and_quantile():
    sk = DDSketch()
    for i in range(1000):
        sk.add(i)
    assert 450 < sk.quantile(0.5) < 550

def test_merge():
    a = DDSketch()
    b = DDSketch()
    a.add(10)
    b.add(20)
    m = a.merge(b)
    assert m.quantile(0.5) > 0