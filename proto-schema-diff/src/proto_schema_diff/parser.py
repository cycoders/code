import os
import subprocess
import tempfile
from pathlib import Path
from typing import List

from google.protobuf.descriptor_pb2 import FileDescriptorSet


def parse_proto_dir(
    proto_dir: Path, include_dirs: List[Path] = None
) -> FileDescriptorSet:
    """Parse .proto files in dir using protoc to FileDescriptorSet."""
    if include_dirs is None:
        include_dirs = []

    proto_files = list(proto_dir.rglob("*.proto"))
    if not proto_files:
        raise ValueError(f"No .proto files found in {proto_dir}")

    with tempfile.NamedTemporaryFile(suffix=".pb", delete=False) as tmpf:
        pb_path = Path(tmpf.name)

    try:
        cmd = [
            "protoc",
            "--descriptor_set_out=" + str(pb_path),
            "--include_imports",
            "--include_source_info",
        ]
        for inc in include_dirs:
            cmd.extend(["-I", str(inc)])
        cmd.extend(str(f) for f in proto_files)

        proc = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        with open(pb_path, "rb") as f:
            return FileDescriptorSet.FromString(f.read())
    finally:
        os.unlink(pb_path)


def parse_descriptor_pb(pb_path: Path) -> FileDescriptorSet:
    """Load pre-compiled descriptor .pb file."""
    with open(pb_path, "rb") as f:
        return FileDescriptorSet.FromString(f.read())
