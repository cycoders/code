import pytest
from pathlib import Path

from dockerfile_optimizer.parser import parse_dockerfile, Instruction


@pytest.fixture
def simple_df(tmp_path: Path) -> Path:
    df = tmp_path / "Dockerfile"
    df.write_text(
        """FROM ubuntu:22.04

RUN apt-get update

# Install
RUN apt-get install -y curl

COPY . /app
"""
    )
    return df


def test_parse_simple(simple_df: Path):
    insts = parse_dockerfile(str(simple_df))
    assert len(insts) == 4
    assert insts[0] == Instruction("FROM", "ubuntu:22.04", 1, "FROM ubuntu:22.04")
    assert "apt-get update" in insts[1].args
    assert insts[3].command == "COPY"


def test_parse_comments_ignored(tmp_path: Path):
    df = tmp_path / "Dockerfile"
    df.write_text("FROM alpine # base\nRUN echo hi #comment")
    insts = parse_dockerfile(str(df))
    assert len(insts) == 2
    assert "# base" not in insts[0].args


def test_empty_file(tmp_path: Path):
    df = tmp_path / "empty"
    df.touch()
    insts = parse_dockerfile(str(df))
    assert len(insts) == 0
