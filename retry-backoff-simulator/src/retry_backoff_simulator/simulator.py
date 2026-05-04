import random

from .models import SimConfig, TrialResult

from .strategies import STRATEGIES


def run_simulation(config: SimConfig) -> list[TrialResult]:
    """Run num_trials simulations."""
    random.seed(config.seed)

    results = []
    seq_len = len(config.failure_sequence) if config.failure_sequence else 0

    for trial_id in range(config.num_trials):
        strategy_cls = STRATEGIES[config.backoff.strategy]
        strategy = strategy_cls(
            config.backoff.base_delay,
            config.backoff.max_delay,
            config.backoff.factor,
        )

        total_time = 0.0
        attempts = 0
        success = False

        while attempts < config.backoff.max_attempts:
            attempts += 1

            # Determine failure
            if config.failure_sequence and seq_len > 0:
                is_failure = config.failure_sequence[(attempts - 1) % seq_len]
            else:
                is_failure = random.random() < config.failure_rate

            if not is_failure:
                total_time += config.service_time
                success = True
                break
            else:
                delay = strategy.next_delay(attempts)
                total_time += delay

        results.append(TrialResult(total_time=total_time, attempts=attempts, success=success))

    return results
