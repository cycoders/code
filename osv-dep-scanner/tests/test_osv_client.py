import json
from unittest.mock import patch

import pytest
import requests_mock
from packaging.version import Version

from osv_dep_scanner.osv_client import _is_version_affected, scan_lockfile


@pytest.mark.parametrize(
    "dep_ver_str,events,expected",
    [
        ("1.1.0", [">=1.0.0", "<1.2.0"], True),
        ("1.3.0", [">=1.0.0", "<1.2.0"], False),
        ("1.0.0", ["=1.0.0"], True),
        ("1.0.1", ["=1.0.0"], False),
    ],
)
def test_is_version_affected(dep_ver_str: str, events: list[str], expected: bool):
    aff = {"ranges": [{"events": events}]}
    assert _is_version_affected(Version(dep_ver_str), aff) == expected


def test_scan_lockfile_osv_error():
    with requests_mock.Mocker() as m:
        m.post("https://api.osv.dev/v1/query", status_code=500)
        with pytest.raises(RuntimeError, match="Failed to query OSV"):
            scan_lockfile(Path("fake.lock"))


SAMPLE_OSV_RESP = {
    "vulns": [
        {
            "id": "GHSA-1234",
            "summary": "Test vuln",
            "severity": "HIGH",
            "affected": [
                {
                    "package": {"ecosystem": "npm", "name": "lodash"},
                    "ranges": [{"type": "SEMVER", "events": [">=4.0.0", "<4.17.22"]}],
                }
            ],
        }
    ]
}


def test_query_osv_match(tmp_path):
    # Mock deps
    with patch("osv_dep_scanner.osv_client.parse_lockfile", return_value=[{"ecosystem": "npm", "name": "lodash", "version": "4.17.21"}]):
        with requests_mock.Mocker() as m:
            m.post("https://api.osv.dev/v1/query", json=SAMPLE_OSV_RESP)
            result = scan_lockfile(tmp_path / "lock.json")
            assert len(result) == 1
            assert "HIGH" in str(result)