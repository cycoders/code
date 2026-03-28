from typing import Dict, List, Tuple

from google.protobuf import descriptor_pb2

from .models import ChangeType, DiffNode, DiffResult


def diff_sets(old_set: descriptor_pb2.FileDescriptorSet, new_set: descriptor_pb2.FileDescriptorSet) -> DiffResult:
    old_files: Dict[str, descriptor_pb2.FileDescriptorProto] = {f.name: f for f in old_set.file}
    new_files: Dict[str, descriptor_pb2.FileDescriptorProto] = {f.name: f for f in new_set.file}

    all_files = set(old_files) | set(new_files)
    changes: DiffResult = []

    for fname in sorted(all_files):
        old_file = old_files.get(fname)
        new_file = new_files.get(fname)
        file_node = _diff_file(old_file, new_file, fname)
        changes.append(file_node)

    return changes


def _diff_file(
    old: descriptor_pb2.FileDescriptorProto, new: descriptor_pb2.FileDescriptorProto, path: str
) -> DiffNode:
    node = DiffNode(path=path, kind="file", change_type=_determine_change_type(old, new))

    # Diff messages
    old_msgs = {m.name: m for m in (old.message_type if old else [])}
    new_msgs = {m.name: m for m in (new.message_type if new else [])}
    all_msgs = set(old_msgs) | set(new_msgs)
    for mname in sorted(all_msgs):
        old_m = old_msgs.get(mname)
        new_m = new_msgs.get(mname)
        msg_node = _diff_message(old_m, new_m, f"{path}.{mname}")
        node.children.append(msg_node)

    # Diff enums (simplified)
    old_enums = {e.name: e for e in (old.enum_type if old else [])}
    new_enums = {e.name: e for e in (new.enum_type if new else [])}
    all_enums = set(old_enums) | set(new_enums)
    for ename in sorted(all_enums):
        old_e = old_enums.get(ename)
        new_e = new_enums.get(ename)
        enum_node = _diff_enum(old_e, new_e, f"{path}.{ename}")
        node.children.append(enum_node)

    return node


def _diff_message(old: descriptor_pb2.DescriptorProto, new: descriptor_pb2.DescriptorProto, path: str) -> DiffNode:
    node = DiffNode(path=path, kind="message", change_type=_determine_change_type(old, new))

    # Diff fields
    old_fields = {f.name: f for f in (old.field if old else [])}
    new_fields = {f.name: f for f in (new.field if new else [])}
    all_fields = set(old_fields) | set(new_fields)
    for fname in sorted(all_fields):
        old_f = old_fields.get(fname)
        new_f = new_fields.get(fname)
        field_node = _diff_field(old_f, new_f, f"{path}.{fname}")
        node.children.append(field_node)

    # Recurse nested messages (simplified, assume flat for demo)
    return node


def _diff_enum(old: descriptor_pb2.EnumDescriptorProto, new: descriptor_pb2.EnumDescriptorProto, path: str) -> DiffNode:
    node = DiffNode(path=path, kind="enum", change_type=_determine_change_type(old, new))
    # Diff enum values (todo: implement)
    return node


def _diff_field(old: descriptor_pb2.FieldDescriptorProto, new: descriptor_pb2.FieldDescriptorProto, path: str) -> DiffNode:
    old_type = (old.type if old else 0, old.type_name if old else "")
    new_type = (new.type if new else 0, new.type_name if new else "")
    change_type = ChangeType.UNCHANGED
    if not old:
        change_type = ChangeType.ADDED
    elif not new:
        change_type = ChangeType.REMOVED
    elif old_type != new_type or (old.label if old else 0) != (new.label if new else 0):
        change_type = ChangeType.MODIFIED

    return DiffNode(
        path=path,
        kind="field",
        change_type=change_type,
        old_value=old_type,
        new_value=new_type,
    )


def _determine_change_type(old: object, new: object) -> ChangeType:
    if old is None:
        return ChangeType.ADDED
    if new is None:
        return ChangeType.REMOVED
    # Simplified: if any child changed, modified
    return ChangeType.MODIFIED  # Placeholder, refine based on children in full impl
