import textwrap
from pathlib import Path

from i18n_extractor.types import Message
from i18n_extractor.writer import write_po, PO_HEADER


def test_write_po(tmp_path):
    output = tmp_path / "test.pot"
    messages = [
        Message("hello", location=("file.py", 10)),
        Message("goodbye {name}", plural="goodbyes {name}", location=("file.py", 20)),
    ]
    write_po(messages, output)

    content = output.read_text()
    assert PO_HEADER in content
    assert '# : file.py:10' in content
    assert 'msgid "hello"' in content
    assert 'msgstr ""' in content
    assert '# : file.py:20' in content
    assert 'msgid "goodbye {name}"' in content
    assert 'msgid_plural "goodbyes {name}"' in content
