import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_data() -> pd.DataFrame:
    data = [
        {'timestamp': '2024-01-01T00:00:00Z', 'status': 200, 'latency_ms': 100},
        {'timestamp': '2024-01-01T00:01:00Z', 'status': 500, 'latency_ms': 600},
        {'timestamp': '2024-01-01T00:02:00Z', 'status': 200, 'latency_ms': 120},
        {'timestamp': '2024-01-01T00:03:00Z', 'status': 200, 'latency_ms': 110},
        {'timestamp': '2024-01-01T00:04:00Z', 'status': 429, 'latency_ms': 200},
    ]
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.set_index('timestamp')
