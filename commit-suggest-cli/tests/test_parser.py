import pytest
from commit_suggest_cli.parser import parse_diff_text, get_diff_text


def test_parse_diff_text_single_file_add():
    diff = """diff --git a/src/foo.py b/src/foo.py
index 0000000..1111111
--- /dev/null
+++ b/src/foo.py
@@ -0,0 +1 @@
+def hello():
"""
    changes = parse_diff_text(diff)
    assert changes["files"] == ["src/foo.py"]
    assert changes["added_lines"] == ["def hello():"]
    assert changes["removed_lines"] == []


def test_parse_diff_text_modify():
    diff = """diff --git a/src/bar.py b/src/bar.py
@@ -1 +1,2 @@
-def old():
+def new(a):
+    pass
"""
    changes = parse_diff_text(diff)
    assert changes["files"] == ["src/bar.py"]
    assert "def new(a):" in changes["added_lines"]
    assert "def old():" in changes["removed_lines"]


def test_parse_diff_text_multiple_files():
    diff = """diff --git a/a.py b/a.py
+add a

diff --git a/b.py b/b.py
+add b
"""
    changes = parse_diff_text(diff)
    assert changes["files"] == ["a.py", "b.py"]
    assert len(changes["added_lines"]) == 2


def test_parse_diff_text_no_changes():
    changes = parse_diff_text("")
    assert changes["files"] == []
    assert changes["added_lines"] == []


def test_parse_diff_text_ignore_metadata():
    diff = """diff --git a/c.py b/c.py
--- a/c.py
+++ b/c.py
+code
"""
    changes = parse_diff_text(diff)
    assert changes["files"] == ["c.py"]
    assert "code" in changes["added_lines"]
