from typing import List

STRATEGY_STEPS: dict[str, List[int]] = {
    "canary-conservative": [10, 25, 50, 75, 100],
    "canary-aggressive": [25, 50, 75, 100],
    "big-bang": [100],
}


def get_strategy_steps(strategy: str) -> List[int]:
    """Get steps for strategy name or custom '10,30,100'."""
    if strategy.startswith('custom:'):
        steps_str = strategy[7:]
        return [int(s.strip()) for s in steps_str.split(',') if s.strip()]
    if strategy in STRATEGY_STEPS:
        return STRATEGY_STEPS[strategy][:]
    valid = ', '.join(STRATEGY_STEPS)
    raise ValueError(f'Unknown strategy "{strategy}". Use: {valid} or custom:10,50,100')