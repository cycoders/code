import re
import codecs
from pathlib import Path
from typing import Set
from bs4 import BeautifulSoup
import cssutils

cssutils.log.setLevel(60)  # Suppress cssutils logs

HTML_EXTS = {'.html', '.htm', '.xhtml', '.svelte', '.vue', '.astro'}
CSS_EXTS = {'.css'}
JS_EXTS = {'.js', '.jsx', '.ts', '.tsx'}

STRING_PATTERNS = [
    r'"(?:[^"\\]|\\.)*"',
    r'\'([ ^'\\]|\\.)*\'',
    r'`(?:[^`\\]|\\.)*`',
]

def unescape_string(s: str) -> str:
    """Unescape JS/CSS string (\\uXXXX, \\xXX)."""
    try:
        return codecs.decode(s, 'unicode-escape')
    except ValueError:
        return s

def extract_js_strings(content: str) -> Set[int]:
    glyphs = set()
    for pattern in STRING_PATTERNS:
        for match in re.finditer(pattern, content, re.DOTALL):
            raw = match.group(0)
            if len(raw) < 2:
                continue
            s = raw[1:-1]
            s = unescape_string(s)
            glyphs.update(ord(c) for c in s)
    return glyphs

def extract_css_strings(content: str) -> Set[int]:
    return extract_js_strings(content)  # CSS strings similar

def extract_html_text(content: str) -> Set[int]:
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return {ord(c) for c in text}

def extract_glyphs_from_file(file_path: Path) -> Set[int]:
    try:
        content = file_path.read_text('utf-8', errors='ignore')
    except Exception:
        return set()

    suffix = file_path.suffix.lower()
    glyphs: Set[int] = set()

    if suffix in HTML_EXTS:
        glyphs |= extract_html_text(content)
    elif suffix in CSS_EXTS:
        glyphs |= extract_css_strings(content)
        try:
            sheet = cssutils.parseString(content)
            for rule in sheet:
                if hasattr(rule, 'style'):
                    for prop in rule.style:
                        if prop.name == 'content':
                            glyphs |= extract_js_strings(prop.value or '')
        except Exception:
            pass  # Graceful
    elif suffix in JS_EXTS:
        glyphs |= extract_js_strings(content)

    # Filter control chars, keep printable
    glyphs = {cp for cp in glyphs if 32 <= cp <= 0x10FFFF and chr(cp).isprintable()}

    return glyphs

def extract_glyphs_from_dir(input_dir: Path, extensions: list[str]) -> Set[int]:
    glyph_exts = set(extensions)
    all_glyphs: Set[int] = set()

    for file_path in input_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in glyph_exts:
            file_glyphs = extract_glyphs_from_file(file_path)
            all_glyphs |= file_glyphs

    return all_glyphs