import pytest
import pathlib
from local_hosts_manager.hosts import HostsManager, HostEntry


class TestHostsManager:
    @pytest.fixture
    def hm(self, mock_hosts_path):
        hm = HostsManager()
        hm.path = mock_hosts_path
        return hm

    def test_load_empty(self, hm, mock_hosts_path):
        hm.load()
        assert len(hm.lines) == 1
        assert hm.lines[0]["type"] == "comment"

    def test_load_sample(self, hm, mock_hosts_path):
        mock_hosts_path.write_text(
            """
# System comment
127.0.0.1 localhost

127.0.0.1 myapp.local # dev
::1 localhost6\t\t# ipv6 comment
192.168.0.1 invalid_domain
# Invalid ip 999.1.2.3 example.com
\n    blank line after
"""
        )
        hm.load()
        hosts = [l for l in hm.lines if l["type"] == "host"]
        assert len(hosts) == 3
        assert hosts[0]["entry"].ip == "127.0.0.1"
        assert hosts[0]["entry"].domains == ["localhost"]
        assert hosts[1]["entry"].comment == "dev"
        assert hosts[2]["entry"].ip == "::1"
        assert hosts[2]["entry"].domains == ["localhost6"]
        invalids = [l for l in hm.lines if l["type"] == "invalid"]
        assert len(invalids) == 2

    def test_add_new(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 localhost")
        hm.load()
        hm.add("127.0.0.1", ["test.local"], "test")
        hm.save()
        content = mock_hosts_path.read_text()
        assert "127.0.0.1\ttest.local\t# test" in content

    def test_add_existing_ip(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 localhost")
        hm.load()
        hm.add("127.0.0.1", ["myapp.local"])
        assert len(hm.lines[0]["entry"].domains) == 2
        assert "myapp.local" in hm.lines[0]["entry"].domains

    def test_add_invalid_ip(self, hm):
        with pytest.raises(ValueError, match="Invalid IP"):
            hm.add("999.999", ["test.local"])

    def test_add_conflict_force(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 old.local")
        hm.load()
        hm.add("10.0.0.1", ["old.local"], force=True)
        assert any(e.ip == "10.0.0.1" and "old.local" in e.domains for l in hm.lines if l["type"]=="host" for e in [l["entry"]])

    def test_remove(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 localhost myapp.local")
        hm.load()
        hm.remove(["myapp.local"])
        hm.save()
        content = mock_hosts_path.read_text()
        assert "myapp.local" not in content
        assert "localhost" in content

    def test_stats(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 dup.local\n127.0.0.1 dup.local")
        hm.load()
        s = hm.stats()
        assert s["entries"] == 2
        assert s["domains"] == 4
        assert "dup.local" in s["duplicates"]

    def test_validate(self, hm, mock_hosts_path):
        mock_hosts_path.write_text("127.0.0.1 dup.local\n127.0.0.1 dup.local")
        hm.load()
        errors = hm.validate()
        assert len(errors) == 1
        assert "dup.local" in errors[0]

    def test_backup_dir(self, hm, tmp_path):
        hm.path = tmp_path / "hosts"
        backup = hm.backup()
        assert backup.exists()
        assert backup.parent == hm.backup_dir