import time
from shell_recorder_cli.recorder import Recorder


def test_log_reader(tmp_path):
    rec = Recorder(cols=100, rows=20)
    lr = rec.LogReader(rec)

    start = time.time()
    lr.write("hello\n")
    lr.write("world\n")

    assert len(rec.events) == 2
    assert rec.events[0]["stdout"] == "hello\n"
    assert rec.events[1]["stdout"] == "world\n"
    assert rec.duration > 0


def test_recorder_save(tmp_path):
    rec = Recorder()
    rec.events = [{"time": 0.1, "stdout": "test"}]
    rec.duration = 0.1
    rec.start_time = 1730000000.0
    path = tmp_path / "test.shellrec"
    rec._save(path)

    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data[0]["duration"] == 0.1
    assert len(data) == 2
