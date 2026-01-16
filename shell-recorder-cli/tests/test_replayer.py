import sys
from io import StringIO

import pytest
from shell_recorder_cli.replayer import Replayer


@pytest.mark.parametrize("speed", [1.0, 10.0])
def test_replayer(sample_session, speed, capsys):
    r = Replayer(sample_session)
    r.run(speed=speed)

    captured = capsys.readouterr()
    assert "REC> ls" in captured.out
    assert "file1.txt  demo/" in captured.out
    assert "Session replay complete" in captured.out


def test_replayer_missing(sample_session, tmp_path, capsys):
    bad_path = tmp_path / "missing.shellrec"
    with pytest.raises(FileNotFoundError):
        Replayer(bad_path)
