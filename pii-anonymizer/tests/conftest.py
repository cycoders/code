import pytest
import pandas as pd
from typer.testing import CliRunner

from pii_anonymizer.cli import app

runner = CliRunner()

@pytest.fixture
def sample_df():
    data = {
        "name": ["John Doe", "Jane Smith"],
        "email": ["john@example.com", "jane@fake.org"],
        "phone": ["(555) 123-4567", "+1-555-987-6543"],
        "ssn": ["123-45-6789", "987-65-4321"],
        "address": ["123 Main St, NYC", "456 Oak Ave"],
        "safe": ["data", "safe"]
    }
    return pd.DataFrame(data)
