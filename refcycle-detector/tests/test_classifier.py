from refcycle_detector.classifier import CycleType

def test_cycle_types():
    assert CycleType.CONTAINER.value == "container"