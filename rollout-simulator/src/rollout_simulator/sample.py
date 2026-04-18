from datetime import datetime, timedelta


SAMPLE_METRICS = [
    # v1.0.0: stable ~0.008
    {'timestamp': (datetime(2024, 7, 1) + timedelta(minutes=i*5)).isoformat() + 'Z', 'deploy_id': 'v1.0.0', 'traffic_pct': 100.0, 'error_rate': 0.007 + 0.001 * (i%3)/10} for i in range(10)
] + [
    # v1.1.0: minor +0.001
    {'timestamp': (datetime(2024, 7, 2) + timedelta(minutes=i*5)).isoformat() + 'Z', 'deploy_id': 'v1.1.0', 'traffic_pct': 100.0, 'error_rate': 0.009 + 0.0005 * (i%4)/10} for i in range(8)
] + [
    # v1.2.0: spike +0.004
    {'timestamp': (datetime(2024, 7, 3) + timedelta(minutes=i*5)).isoformat() + 'Z', 'deploy_id': 'v1.2.0', 'traffic_pct': 100.0, 'error_rate': 0.012 + 0.002 * (i%5)/10} for i in range(7)
] + [
    # v1.3.0: recovery -0.005
    {'timestamp': (datetime(2024, 7, 4) + timedelta(minutes=i*5)).isoformat() + 'Z', 'deploy_id': 'v1.3.0', 'traffic_pct': 100.0, 'error_rate': 0.007 + 0.0008 * (i%6)/10} for i in range(5)
]


def generate_sample() -> str:
    """Generate sample metrics JSONL string."""
    lines = [json.dumps(entry) for entry in SAMPLE_METRICS]
    return '\n'.join(lines) + '\n'