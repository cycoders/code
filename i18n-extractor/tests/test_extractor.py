import ast
from pathlib import Path

import pytest
from i18n_extractor.extractor import Extractor, scan_file
from i18n_extractor.types import Message


@pytest.fixture
def extractor():
    return Extractor({"_"}, {"ngettext"})


class TestExtractor:
    def test_literal_string(self, extractor):
        code = "_('hello world')"
        tree = ast.parse(code)
        extractor.visit(tree)
        assert len(extractor.messages) == 1
        assert extractor.messages[0].singular == "hello world"

    def test_fstring(self, extractor):
        code = "_('hello {name}')"  # simulates f-string template
        tree = ast.parse(code)
        extractor.visit(tree)
        assert extractor.messages[0].singular == "hello {name}"

    def test_joinedstr(self, extractor):
        code = "_('hello ' + '{}')"  # approx f"hello {var}"
        tree = ast.parse(code)
        extractor.visit(tree)
        assert extractor.messages[0].singular == "hello "  # partial

    def test_format_call(self, extractor):
        code = "_('hello {name}'.format(name='arya'))"
        tree = ast.parse(code)
        extractor.visit(tree)
        assert extractor.messages[0].singular == "hello {name}"

    def test_plural(self, extractor):
        code = "ngettext('one', 'many', n)"
        tree = ast.parse(code)
        extractor.visit(tree)
        assert len(extractor.messages) == 1
        assert extractor.messages[0].singular == "one"
        assert extractor.messages[0].plural == "many"

    def test_no_match(self, extractor):
        code = "print('not translated')"
        tree = ast.parse(code)
        extractor.visit(tree)
        assert len(extractor.messages) == 0

    def test_syntax_error(self):
        path = Path("test.py")
        path.write_text("invalid syntax")
        msgs = scan_file(path, {"_"}, {"ngettext"})
        assert len(msgs) == 0
