from histogram_merger.ddsketch import DDSketch

from histogram_merger.merge import merge_sketches


def test_merge_multiple():
    sketches = [DDSketch() for _ in range(3)]
    for i, sk in enumerate(sketches):
        sk.add(100 * (i + 1))
    merged = merge_sketches(sketches)
    assert merged.quantile(0.9) > 200