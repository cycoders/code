import pytest
from otel_sampling_advisor.analyzer import TraceAnalyzer

def test_adaptive_strategy_preserves_signals():
    analyzer = TraceAnalyzer()
    result = analyzer.run('traces.json', 'adaptive', 0.15)
    assert result.preserved_signals > 0.9

def test_budget_respected():
    analyzer = TraceAnalyzer()
    result = analyzer.run('traces.json', 'probability', 0.05)
    assert result.cost_reduction > 0.7

def test_config_generation():
    analyzer = TraceAnalyzer()
    result = analyzer.run('traces.json', 'adaptive', 0.1)
    assert 'probabilistic_sampler' in result.config_snippet