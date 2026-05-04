import matplotlib.pyplot as plt

from typing import List

from .models import TrialResult


def plot_simulation(results: List[TrialResult], output_file: str):
    """Generate diagnostic plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Retry Simulation Analysis", fontsize=16)

    attempts = [r.attempts for r in results]
    times = [r.total_time for r in results]
    success_times = [r.total_time for r in results if r.success]

    # Attempts histogram
    ax1.hist(attempts, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
    ax1.set_title("Attempts Distribution")
    ax1.set_xlabel("Attempts")
    ax1.set_ylabel("Frequency")

    # Total time histogram (all)
    ax2.hist(times, bins=30, alpha=0.7, color="lightgreen", edgecolor="black")
    ax2.set_title("Total Time Distribution (All Trials)")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Frequency")

    # Success time CDF
    if success_times:
        sorted_times = sorted(success_times)
        n = len(sorted_times)
        cdf_y = [i / n for i in range(1, n + 1)]
        ax3.plot(sorted_times, cdf_y, linewidth=2, color="darkblue")
        ax3.set_title("Recovery Time CDF (Successes Only)")
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Cumulative Probability")
        ax3.grid(True, alpha=0.3)

    # Attempts vs Time scatter
    colors = ["red" if not r.success else "green" for r in results]
    ax4.scatter(attempts, times, c=colors, alpha=0.6, s=20)
    ax4.set_title("Attempts vs Total Time")
    ax4.set_xlabel("Attempts")
    ax4.set_ylabel("Time (s)")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()


def plot_comparison(metrics_list: List["Metrics"], output_file: str):
    """Compare multiple sims (placeholder for multi-plot)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [m.name or f"Sim {i+1}" for i, m in enumerate(metrics_list)]
    p95_times = [m.p95_time for m in metrics_list]
    avg_attempts_list = [m.avg_attempts for m in metrics_list]

    x = range(len(names))
    width = 0.35

    ax.bar([i - width/2 for i in x], p95_times, width, label="P95 Time (s)")
    ax.bar([i + width/2 for i in x], avg_attempts_list, width, label="Avg Attempts")

    ax.set_title("Strategy Comparison")
    ax.set_xlabel("Strategies")
    ax.set_ylabel("Values")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
