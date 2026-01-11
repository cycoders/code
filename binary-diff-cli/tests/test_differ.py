import os

from binary_diff_cli.differ import compare_paths, bytes_to_hex_ascii, get_file_sizes


class TestBytesToHexAscii:
    def test_basic(self):
        b = b"abc\x00\xff"
        hexs, asc = bytes_to_hex_ascii(b)
        assert hexs == "61 62 63 00 ff"
        assert asc == "abc.."

    def test_empty(self):
        assert bytes_to_hex_ascii(b"") == ("", "")


class TestComparePaths:
    def test_identical(self, tmp_bins):
        f1, f2_same, _, _ = tmp_bins  # make same
        f2_same.write_bytes(f1.read_bytes())
        blocks = list(compare_paths(f1, f2_same))
        assert len(blocks) == 6  # 90//16=5 + partial
        assert all(b["changes"] == 0 for b in blocks)
        assert all(len(b["diff_positions"]) == 0 for b in blocks)

    def test_all_changes(self, tmp_path):
        f1 = tmp_path / "f1"
        f2 = tmp_path / "f2"
        f1.write_bytes(b"\x00" * 32)
        f2.write_bytes(b"\xff" * 32)
        blocks = list(compare_paths(f1, f2))
        assert blocks[0]["changes"] == 16
        assert blocks[1]["changes"] == 16

    def test_short_files(self, tmp_bins):
        f_long, _, f_short, _ = tmp_bins
        blocks = list(compare_paths(f_short, f_long))
        assert len(blocks) == 2  # 30//16=1 +14
        assert all(b["changes"] == 0 for b in blocks)

    def test_empty(self, tmp_bins):
        _, _, _, f_empty = tmp_bins
        blocks = list(compare_paths(f_empty, f_empty))
        assert len(blocks) == 0


class TestFileSizes:
    def test_basic(self, tmp_bins):
        f1, _, _, _ = tmp_bins
        s1, _ = get_file_sizes(f1, f1)
        assert s1 == 90
