import pytest
from migration_safety_analyzer.analyzer import analyze_migrations

def test_basic():
    assert analyze_migrations('migrations/', None, 'postgres')['risk_score'] >= 0