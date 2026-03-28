import pytest
from google.protobuf.descriptor_pb2 import FileDescriptorSet

from proto_schema_diff.parser import parse_descriptor_pb


def test_parse_descriptor_pb(tmp_path):
    # Create a minimal valid pb (serialized manually for test)
    set_pb = FileDescriptorSet()
    file_pb = set_pb.file.add()
    file_pb.name = "test.proto"
    pb_bytes = set_pb.SerializeToString()

    pb_path = tmp_path / "test.pb"
    pb_path.write_bytes(pb_bytes)

    parsed = parse_descriptor_pb(pb_path)
    assert len(parsed.file) == 1
    assert parsed.file[0].name == "test.proto"
