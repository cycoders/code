import pytest
from google.protobuf import descriptor_pb2

from proto_schema_diff.differ import diff_sets
from proto_schema_diff.models import ChangeType, DiffNode


@pytest.fixture
def simple_old_set():
    old_set = descriptor_pb2.FileDescriptorSet()
    old_file = old_set.file.add()
    old_file.name = "user.proto"
    old_msg = old_file.message_type.add()
    old_msg.name = "User"
    old_field = old_msg.field.add()
    old_field.name = "name"
    old_field.number = 1
    old_field.label = descriptor_pb2.LABEL_OPTIONAL
    old_field.type = descriptor_pb2.TYPE_STRING
    return old_set


@pytest.fixture
def simple_new_set(simple_old_set):
    new_set = descriptor_pb2.FileDescriptorSet()
    new_file = new_set.file.add()
    new_file.name = "user.proto"
    new_msg = new_file.message_type.add()
    new_msg.name = "User"
    # Modified: name -> id
    new_field = new_msg.field.add()
    new_field.name = "id"
    new_field.number = 1
    new_field.label = descriptor_pb2.LABEL_OPTIONAL
    new_field.type = descriptor_pb2.TYPE_INT64
    return new_set


def test_diff_sets(simple_old_set, simple_new_set):
    diffs = diff_sets(simple_old_set, simple_new_set)
    assert len(diffs) == 1
    assert diffs[0].path == "user.proto"
    assert diffs[0].kind == "file"
    assert len(diffs[0].children) == 1  # message
    msg_node = diffs[0].children[0]
    assert msg_node.path.endswith(".User")
    assert msg_node.kind == "message"
    field_node = msg_node.children[0]
    assert field_node.kind == "field"
    assert field_node.change_type == ChangeType.MODIFIED


def test_added_file():
    old_set = descriptor_pb2.FileDescriptorSet()
    new_set = descriptor_pb2.FileDescriptorSet()
    new_file = new_set.file.add()
    new_file.name = "new.proto"
    diffs = diff_sets(old_set, new_set)
    assert len(diffs) == 1
    assert diffs[0].change_type == ChangeType.ADDED
