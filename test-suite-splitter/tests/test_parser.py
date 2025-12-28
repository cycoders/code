import pytest
from pathlib import Path
from test_suite_splitter.parser import parse_junit_files, iter_junit_paths


class TestParser:
    def test_parse_sample(self, sample_xml: Path) -> None:
        tests = parse_junit_files([sample_xml])
        assert len(tests) == 5
        assert tests[0].suite == "slow"
        assert tests[0].name == "slow1"
        assert tests[0].duration == 2.5
        assert all(t.duration >= 0 for t in tests)

    def test_parse_empty(self, empty_xml: Path) -> None:
        tests = parse_junit_files([empty_xml])
        assert len(tests) == 0

    def test_parse_invalid_graceful(self, invalid_xml: Path) -> None:
        tests = parse_junit_files([invalid_xml])
        assert len(tests) == 0  # no crash

    def test_iter_junit_paths_files(self, sample_xml: Path) -> None:
        paths = list(iter_junit_paths([sample_xml]))
        assert len(paths) == 1
        assert paths[0] == sample_xml

    def test_iter_junit_paths_dir(self, tmp_path: Path, sample_xml: Path) -> None:
        dir_path = tmp_path / "artifacts"
        dir_path.mkdir()
        sample_xml.replace(dir_path / "TEST-results.xml")
        paths = list(iter_junit_paths([dir_path]))
        assert len(paths) == 1
        assert paths[0].name == "TEST-results.xml"

    def test_non_matching_files_ignored(self, tmp_path: Path) -> None:
        (tmp_path / "not-junit.txt").touch()
        (tmp_path / "config.xml").touch()
        paths = list(iter_junit_paths([tmp_path]))
        assert len(paths) == 0