import csv
from pathlib import Path
from typing import List

from .types import Message

PO_HEADER = '''msgid ""
msgstr ""
"Project-Id-Version: 0.1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-01-01 00:00+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: i18n-extractor 0.1.0\\n"

'''

def escape_po(s: str) -> str:
    """Escape string for PO format."""
    s = s.replace('\\', '\\\\').replace('\"', '\\"').replace('\n', '\\n')
    return s

def write_po(messages: List[Message], output_path: Path) -> None:
    """Write messages to PO file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(PO_HEADER)
        for msg in messages:
            file_line = f"{msg.location[0]}:{msg.location[1]}"
            f.write(f'# : {file_line}\n')
            f.write(f'msgid "{escape_po(msg.singular)}"\n')
            f.write('msgstr ""\n')
            if msg.plural:
                f.write(f'msgid_plural "{escape_po(msg.plural)}"\n')
                f.write('msgstr[0] ""\n')
                f.write('msgstr[1] ""\n')
            f.write("\n")