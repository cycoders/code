from dotenv_linter.parser import Entry
from dotenv_linter.rules import duplicate_keys

def test_duplicate_detection():
    entries = [Entry("A", "1", 1, ""), Entry("A", "2", 2, "")]
    assert len(duplicate_keys(entries)) == 1