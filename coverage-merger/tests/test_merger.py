import pytest
from pathlib import Path
from coverage_merger.merger import (
    parse_coverage_xml,
    merge_reports,
    compute_stats,
    write_xml,
)


class TestParser:
    def test_parse_basic(self, sample_xml1: Path):
        data = parse_coverage_xml(sample_xml1)
        assert len(data) == 1
        fdata = data["file.py"]
        assert fdata["covered_lines"] == {1, 3}
        assert fdata["possible_lines"] == {1, 2, 3}
        assert fdata["covered_branches"] == {3}
        assert fdata["possible_branches"] == {3}

    def test_parse_no_branches(self, sample_xml2: Path):
        data = parse_coverage_xml(sample_xml2)
        fdata = data["file.py"]
        assert fdata["covered_lines"] == {2}
        assert fdata["possible_lines"] == {2, 4}
        assert fdata["covered_branches"] == set()
        assert fdata["possible_branches"] == set()

    def test_parse_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.xml"
        p.write_text('<coverage/>')
        data = parse_coverage_xml(p)
        assert data == {}


class TestMerger:
    def test_merge_two_reports(self, sample_xml1: Path, sample_xml2: Path):
        merged = merge_reports([sample_xml1, sample_xml2])
        assert len(merged) == 1
        fdata = merged["file.py"]
        assert fdata["covered_lines"] == {1, 2, 3}
        assert fdata["possible_lines"] == {1, 2, 3, 4}
        assert fdata["covered_branches"] == {3}
        assert fdata["possible_branches"] == {3}

    def test_stats_computation(self, sample_xml1: Path, sample_xml2: Path):
        merged = merge_reports([sample_xml1, sample_xml2])
        stats = compute_stats(merged)
        assert len(stats) == 1
        stat = stats[0]
        assert stat["file"] == "file.py"
        assert stat["line_pct"] == 75.0
        assert stat["branch_pct"] == 100.0
        assert stat["missed_lines"] == 1

    def test_write_xml(self, tmp_path: Path, sample_xml1: Path, sample_xml2: Path):
        merged = merge_reports([sample_xml1, sample_xml2])
        out = tmp_path / "merged.xml"
        write_xml(merged, out)
        assert out.exists()
        tree = ET.parse(out)
        cls = tree.findall(".//class")[0]
        assert cls.get("filename") == "file.py"
        assert cls.get("lines") == "4"
        assert "75.00" in cls.get("line_rates", "")


class TestEdgeCases:
    def test_no_inputs(self):
        with pytest.raises(ValueError):
            merge_reports([])  # Would be caught in CLI

    def test_missing_file(self, tmp_path: Path):
        bad_path = tmp_path / "missing.xml"
        with pytest.raises(FileNotFoundError):
            merge_reports([bad_path])
