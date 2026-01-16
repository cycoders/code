from shell_recorder_cli.editor import parse_line_ranges, delete_lines


class TestParseLineRanges:
    def test_single(self):
        assert parse_line_ranges("2") == [1]
        assert parse_line_ranges("1,3") == [0, 2]

    def test_range(self):
        assert parse_line_ranges("1-3") == [0, 1, 2]
        assert parse_line_ranges("2,5-7") == [1, 4, 5, 6]

    def test_dedupe(self):
        assert parse_line_ranges("1-3,2") == [0, 1, 2]

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_line_ranges("abc")


def test_delete_lines(sample_session, tmp_path):
    out = tmp_path / "edited.shellrec"
    delete_lines(sample_session, out, [0, 2])  # remove ls and exit

    with open(out) as f:
        data = json.load(f)
    stdout_all = "".join(e["stdout"] for e in data[1:])
    assert "ls" not in stdout_all
    assert "exit" not in stdout_all
    assert "file1.txt" in stdout_all  # kept
