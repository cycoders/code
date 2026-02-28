import pytest
import tempfile
from pathlib import Path
from scapy.all import Ether, IP, TCP, UDP, wrpcap


@pytest.fixture
def sample_pcap(tmp_path: Path):
    """Create sample PCAP with TCP/UDP bidirectional."""
    pcap_path = tmp_path / "sample.pcap"
    pkts = [
        Ether() / IP(src="192.168.1.1", dst="10.0.0.1") / TCP(sport=54321, dport=80),
        Ether() / IP(src="10.0.0.1", dst="192.168.1.1") / TCP(sport=80, dport=54321),
        Ether() / IP(src="192.168.1.1", dst="8.8.8.8") / UDP(sport=12345, dport=53),
        Ether() / IP(src="8.8.8.8", dst="192.168.1.1") / UDP(sport=53, dport=12345),
        Ether() / IP(src="192.168.1.2") / TCP(),  # Single
    ]
    wrpcap(pcap_path, pkts)
    return pcap_path