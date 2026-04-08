import pytest
from serdes_bench.formats import (
    StdJSONSerializer,
    OrJSONSerializer,
    UJSONSerializer,
    MsgPackSerializer,
    CBORSerializer,
)


SAMPLE = {"key": "val", "list": [1, 2], "bool": True, "num": 3.14}


@pytest.mark.parametrize(
    "ser",
    [
        StdJSONSerializer(),
        OrJSONSerializer(),
        UJSONSerializer(),
        MsgPackSerializer(),
        CBORSerializer(),
    ],
)
def test_all_roundtrip(ser, sample_data: dict):
    ser_bytes = ser.serialize(sample_data)
    assert isinstance(ser_bytes, bytes)
    assert len(ser_bytes) > 0
    roundtrip = ser.deserialize(ser_bytes)
    assert roundtrip == sample_data
