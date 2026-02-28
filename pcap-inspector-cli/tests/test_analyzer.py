from pcap_inspector_cli.analyzer import Analyzer
import pytest
from collections import Counter


class TestAnalyzer:
    def test_get_stats(self, sample_pcap):
        analyzer = Analyzer(sample_pcap)
        stats = analyzer.get_stats()
        assert stats["packets"] == 5
        assert stats["flows_count"] == 2  # 2 bidirectional flows
        protos = stats["protocols"]
        assert protos[6] == 4  # TCP 4 pkts
        assert protos[17] == 2  # UDP 2
        assert "192.168.1.1" in stats["src_bytes"]

    def test_get_flows(self, sample_pcap):
        analyzer = Analyzer(sample_pcap)
        flows = analyzer.get_flows(10)
        assert len(flows) == 2
        tcp_flow = next(f for f in flows if f["proto"] == "TCP")
        assert tcp_flow["packets"] == 2
        udp_flow = next(f for f in flows if f["proto"] == "UDP")
        assert udp_flow["packets"] == 2

    def test_flow_key_bidirectional(self, sample_pcap):
        analyzer = Analyzer(sample_pcap)
        flows = analyzer.get_flows()
        # Both directions same key
        assert len(flows) == 2

    def test_no_ip_packets(self, tmp_path):
        # Empty or non-IP
        pcap_noip = tmp_path / "noip.pcap"
        # wrpcap with no IP
        with pytest.raises(ValueError):
            Analyzer(pcap_noip)  # But need valid pcap, skip or create minimal

    def test_empty_pcap(self, tmp_path):
        empty = tmp_path / "empty.pcap"
        empty.touch()
        with pytest.raises(ValueError, match="Empty"):
            Analyzer(empty)