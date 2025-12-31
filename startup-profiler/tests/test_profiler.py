import os
import sys
from unittest.mock import MagicMock, patch, Mock
from pytest import MonkeyPatch

import pytest
from startup_profiler.profiler import ImportProfiler


class TestImportProfiler:
    def test_init(self):
        p = ImportProfiler()
        assert isinstance(p.timings, dict)
        assert p.timings == {}

    def test_should_skip(self):
        p = ImportProfiler()
        assert p._should_skip("sys")
        assert p._should_skip("startup_profiler.foo")
        assert not p._should_skip("numpy")

    def test_record_timing(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("sysconfig.get_path", lambda x: "/usr/lib/python3.11")
        monkeypatch.setattr("os.path.getsize", lambda x: 10240)
        p = ImportProfiler()
        mock_mod = Mock(__file__="/usr/lib/python3.11/os.py")
        p._record_timing("os", 0.05, mock_mod)
        t = p.timings["os"]
        assert t["total"] == 0.05
        assert t["self"] == 0.05
        assert t["size"] == 10.0
        assert t["is_stdlib"] is True

    def test_record_timing_no_file(self):
        p = ImportProfiler()
        mock_mod = Mock()
        p._record_timing("builtins", 0.01, mock_mod)
        t = p.timings["builtins"]
        assert t["size"] == 0.0
        assert t["is_stdlib"] is False  # no __file__

    def test_parent_child_relation(self):
        p = ImportProfiler()
        p._import_stack = ["parent"]
        p.timings["parent"] = {"children": [], "children_time": 0.0, "total": 0.1}
        mock_mod = Mock()
        p._record_timing("child", 0.03, mock_mod)
        assert "child" in p.timings
        assert p.timings["parent"]["children"] == ["child"]
        assert p.timings["parent"]["children_time"] == 0.03
        assert p.timings["child"]["parent"] == "parent"
        assert p.timings["child"]["self"] == 0.03

    def test_get_timings_meta(self):
        p = ImportProfiler()
        p.timings["root"] = {"parent": None}
        p.timings["child"] = {"parent": "root"}
        timings = p.get_timings()
        assert timings["_meta"]["roots"] == ["root"]
