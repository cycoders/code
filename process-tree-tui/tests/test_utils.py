import psutil
from process_tree_tui.utils import format_node


def test_format_node_happy_path(mock_process):
    label = format_node(mock_process)
    assert "123" in label
    assert "testproc" in label
    assert "1.2%" in label
    assert "100M" in label
    assert "test proc" in label


def test_format_node_error(mock_process):
    mock_process.cpu_percent.side_effect = psutil.AccessDenied
    label = format_node(mock_process)
    assert "✗ 123 [GONE/ZOMBIE]" in label or "? 123 [ERROR]" in label


def test_format_node_long_cmd(mock_process):
    mock_process.cmdline.return_value = ["a"] * 20
    label = format_node(mock_process)
    assert len(label) < 200  # Bounded


def test_format_node_no_cmd(mock_process):
    mock_process.cmdline.return_value = []
    mock_process.name.return_value = "silent"
    label = format_node(mock_process)
    assert "[? unknown]" in label


def test_format_node_zombie():
    p = MagicMock()
    p.pid = 999
    p.cpu_percent.side_effect = psutil.ZombieProcess(999)
    label = format_node(p)
    assert "✗ 999 [GONE/ZOMBIE]" in label