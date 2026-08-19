from __future__ import annotations

from histogram_merger.ddsketch import DDSketch


def merge_sketches(sketches: list[DDSketch]) -> DDSketch:
    if not sketches:
        return DDSketch()
    result = sketches[0]
    for s in sketches[1:]:
        result = result.merge(s)
    return result