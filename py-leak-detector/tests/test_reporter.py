from unittest.mock import MagicMock
from py_leak_detector.reporter import print_report
from py_leak_detector.analyzer import RSSAnalysis, HeapAnalysis, HeapLeak


def test_print_report(capsys):
    rss = RSSAnalysis([50, 80], [0, 5], [30], 30, 6.0, 30, True)
    heap_leak = HeapLeak(10*1024**2, 100, "test.py:10")
    heap = HeapAnalysis([heap_leak], True)

    console = MagicMock()
    print_report(console, rss, heap)

    captured = capsys.readouterr()
    assert "RSS Leak!" in captured.out
    assert "Top Heap Leaks" in captured.out
