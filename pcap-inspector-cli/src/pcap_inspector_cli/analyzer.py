from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Tuple

from scapy.utils import PcapReader
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import NoPayload

PROTO_NAMES = {
    1: "ICMP",
    2: "IGMP",
    6: "TCP",
    17: "UDP",
    47: "GRE",
    50: "ESP",
    51: "AH",
    89: "OSPF",
    115: "L2TP",
}

FlowKey = Tuple[str, str, int, int, int]


class Analyzer:
    """Streaming PCAP analyzer for stats and flows."""

    def __init__(self, pcap_path: Path):
        self.pcap_path = pcap_path
        self._validate_pcap()

    def _validate_pcap(self):
        """Ensure valid PCAP file."""
        try:
            reader = PcapReader(self.pcap_path)
            next(reader)
        except StopIteration:
            raise ValueError("Empty PCAP file")
        except Exception as e:
            raise ValueError(f"Invalid PCAP: {e}")

    def _get_layer(self, pkt: Any, layer: Any) -> Any:
        try:
            return pkt[layer]
        except (KeyError, IndexError):
            return None

    def _flow_key(self, pkt: Any) -> FlowKey:
        ip_layer = self._get_layer(pkt, IP)
        if not ip_layer:
            return None
        proto = ip_layer.proto
        sport = dport = 0
        if proto == 6:
            tcp_layer = self._get_layer(pkt, TCP)
            if tcp_layer:
                sport, dport = tcp_layer.sport, tcp_layer.dport
        elif proto == 17:
            udp_layer = self._get_layer(pkt, UDP)
            if udp_layer:
                sport, dport = udp_layer.sport, udp_layer.dport
        key_fwd = (ip_layer.src, ip_layer.dst, proto, sport, dport)
        key_rev = (ip_layer.dst, ip_layer.src, proto, dport, sport)
        return min(key_fwd, key_rev)

    def get_stats(self) -> Dict[str, Any]:
        packets = bytes_total = 0
        protocols = Counter()
        src_bytes = defaultdict(int)
        dst_bytes = defaultdict(int)
        flows_data = defaultdict(lambda: {"pkts": 0, "bytes": 0, "first_ts": float("inf"), "last_ts": 0.0})

        reader = PcapReader(self.pcap_path)
        for pkt in reader:
            packets += 1
            bytes_total += len(pkt)
            ip_layer = self._get_layer(pkt, IP)
            if ip_layer:
                proto = ip_layer.proto
                protocols[proto] += 1
                src_bytes[ip_layer.src] += len(pkt)
                dst_bytes[ip_layer.dst] += len(pkt)
                flow_key = self._flow_key(pkt)
                if flow_key:
                    flow = flows_data[flow_key]
                    flow["pkts"] += 1
                    flow["bytes"] += len(pkt)
                    flow["first_ts"] = min(flow["first_ts"], pkt.time)
                    flow["last_ts"] = max(flow["last_ts"], pkt.time)

        total_duration = 0.0
        if packets > 0:
            # Approximate total duration from first/last packet
            total_duration = max([f["last_ts"] for f in flows_data.values()] + [0]) - min([f["first_ts"] for f in flows_data.values()] + [0])

        stats = {
            "packets": packets,
            "bytes": bytes_total,
            "avg_size": bytes_total / packets if packets else 0,
            "duration": total_duration,
            "protocols": dict(protocols),
            "src_bytes": dict(src_bytes),
            "dst_bytes": dict(dst_bytes),
            "flows_count": len(flows_data),
        }
        return stats

    def get_flows(self, limit: int = 10) -> List[Dict[str, Any]]:
        flows_data = defaultdict(lambda: {"pkts": 0, "bytes": 0, "first_ts": float("inf"), "last_ts": 0.0})
        reader = PcapReader(self.pcap_path)
        for pkt in reader:
            flow_key = self._flow_key(pkt)
            if flow_key:
                flow = flows_data[flow_key]
                flow["pkts"] += 1
                flow["bytes"] += len(pkt)
                flow["first_ts"] = min(flow["first_ts"], pkt.time)
                flow["last_ts"] = max(flow["last_ts"], pkt.time)

        flows_list = []
        for key, data in flows_data.items():
            src_ip, dst_ip, proto, src_port, dst_port = key
            duration = data["last_ts"] - data["first_ts"] if data["pkts"] > 0 else 0.0
            flows_list.append({
                "src_ip": src_ip,
                "src_port": src_port,
                "dst_ip": dst_ip,
                "dst_port": dst_port,
                "proto": PROTO_NAMES.get(proto, str(proto)),
                "packets": data["pkts"],
                "bytes": data["bytes"],
                "duration": round(duration, 1),
            })
        flows_list.sort(key=lambda f: f["bytes"], reverse=True)
        return flows_list[:limit]