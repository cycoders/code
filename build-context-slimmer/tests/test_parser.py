import pytest
from pathlib import Path

from build_context_slimmer.parser import parse_copy_patterns, dockerfile_content


@pytest.fixture
def simple_df(tmp_path: Path) -> Path:
    df = tmp_path / "Dockerfile"
    df.write_text("COPY src/ app/src/")
    return df


def test_parse_simple(simple_df: Path) -> None:
    patterns = parse_copy_patterns(simple_df)
    assert patterns == ["src/"]


def test_add_command() -> None:
    df = dockerfile_content("""
ADD package.json app/
    """)
    patterns = parse_copy_patterns(df)
    assert patterns == ["package.json"]


def test_flags() -> None:
    df = dockerfile_content("""
COPY --chown=1000:1000 --chmod=755 foo bar/
    """)
    patterns = parse_copy_patterns(df)
    assert patterns == ["foo"]


def test_from_skip() -> None:
    df = dockerfile_content("""
COPY --from=builder /app /usr/
COPY src/ app/
    """)
    patterns = parse_copy_patterns(df)
    assert patterns == ["src/"]


def test_multi_src() -> None:
    df = dockerfile_content("""
COPY *.go config.yaml /app/
    """)
    patterns = parse_copy_patterns(df)
    assert set(patterns) == {"*.go", "config.yaml"}


def test_no_srcs() -> None:
    df = dockerfile_content("COPY /dev/null /")
    patterns = parse_copy_patterns(df)
    assert patterns == []


def test_comments_ignore() -> None:
    df = dockerfile_content("""
# COPY foo bar
RUN echo
COPY src/ app/
    """)
    patterns = parse_copy_patterns(df)
    assert patterns == ["src/"]
