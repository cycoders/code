import re
from typing import List, Dict
from .models import Frame

parsers: Dict[str, callable] = {}


def register_parser(lang: str, parser_fn):
    parsers[lang] = parser_fn


@register_parser("python")
def parse_python(content: str) -> List[Frame]:
    frames = []
    pattern = re.compile(r'File "(.+?)", line (\d+), in (.+)', re.MULTILINE)
    for match in pattern.finditer(content):
        file_path, line_str, func_name = match.groups()
        frames.append(Frame(
            file=file_path,
            line=int(line_str),
            func=func_name.strip(),
        ))
    # Python prints outermost first → reverse for deepest-first
    frames.reverse()
    return frames


@register_parser("nodejs")
def parse_nodejs(content: str) -> List[Frame]:
    frames = []
    pattern = re.compile(
        r'at\s+(?P<func>.+?)\s*\((?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?\)',
        re.MULTILINE,
    )
    for match in pattern.finditer(content):
        frames.append(Frame(
            file=match.group("file"),
            line=int(match.group("line")),
            func=match.group("func").strip(),
            col=int(match.group("col")) if match.group("col") else None,
        ))
    # Node: deepest first
    return frames


@register_parser("java")
def parse_java(content: str) -> List[Frame]:
    frames = []
    pattern = re.compile(r'at\s+(?P<func>.+?)\((?P<file>.+?):(?P<line>\d+)\)', re.MULTILINE)
    for match in pattern.finditer(content):
        frames.append(Frame(
            file=match.group("file"),
            line=int(match.group("line")),
            func=match.group("func").strip(),
        ))
    return frames


@register_parser("go")
def parse_go(content: str) -> List[Frame]:
    frames = []
    pattern = re.compile(r'(?P<file>[^:]+):(?P<line>\d+)\s+\+\S+\s+(?P<func>.+)', re.MULTILINE)
    for match in pattern.finditer(content):
        frames.append(Frame(
            file=match.group("file"),
            line=int(match.group("line")),
            func=match.group("func").strip(),
        ))
    return frames


def detect_language(content: str) -> str:
    content_lower = content.lower()
    if 'file "' in content and 'line ' in content and 'in ' in content:
        return "python"
    if 'at ' in content_lower and any(ext in content for ext in ['.js:', '.ts:', '.mjs:', '.cjs:']):
        return "nodejs"
    if 'at ' in content_lower and '.java:' in content:
        return "java"
    if 'goroutine' in content_lower and '.go:' in content:
        return "go"
    raise ValueError(
        f"Unsupported stack trace language. Content preview: {content[:200]}\n"
        f"Supported: python, nodejs, java, go"
    )


def parse(content: str, language: str) -> List[Frame]:
    """Parse content to frames using language parser."""
    if language not in parsers:
        raise ValueError(f"Unsupported language: {language}")
    return parsers[language](content)
