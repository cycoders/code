from abc import ABC, abstractmethod
from typing import Any, Dict, Type

import orjson
import msgpack
import cbor2
import ujson
import json

from .benchmark import Result


class Serializer(ABC):
    """Protocol for serializers. Stateless, thread-safe."""

    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """Serialize to bytes. Fast path."""
        ...

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to obj. Roundtrip verifiable."""
        ...


class StdJSONSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return json.dumps(obj, separators=(',', ':')).encode('utf-8')

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))


class OrJSONSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return orjson.dumps(obj)

    def deserialize(self, data: bytes) -> Any:
        return orjson.loads(data)


class UJSONSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return ujson.dumps(obj).encode('utf-8')

    def deserialize(self, data: bytes) -> Any:
        return ujson.loads(data.decode('utf-8'))


class MsgPackSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return msgpack.packb(obj, use_bin_type=True, strict_types=True)

    def deserialize(self, data: bytes) -> Any:
        return msgpack.unpackb(data, raw=False, strict_map_key=False)


class CBORSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return cbor2.dumps(obj)

    def deserialize(self, data: bytes) -> Any:
        return cbor2.loads(data)


FORMAT_SERIALIZERS: Dict[str, Serializer] = {
    'json': StdJSONSerializer(),
    'orjson': OrJSONSerializer(),
    'ujson': UJSONSerializer(),
    'msgpack': MsgPackSerializer(),
    'cbor': CBORSerializer(),
}

FORMAT_NAMES = list(FORMAT_SERIALIZERS.keys())


def get_serializer(name: str) -> Serializer:
    ser = FORMAT_SERIALIZERS.get(name)
    if ser is None:
        raise ValueError(f"Unknown format: {name}")
    return ser
