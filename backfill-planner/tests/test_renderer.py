from backfill_planner.renderer import render_plan
import sys
from io import StringIO
from unittest.mock import Mock

from backfill_planner.plan import Plan, Phase


def test_renderer_outputs_plan():
    plan = Plan(
        strategy="online-batched",
        dialect="postgresql",
        total_rows=1000,
        total_est_time_hours=0.1,
        optimal_batch_size=100,
        phases=[Phase(name="Test", description="", est_duration_hours=0.1, batches=10, sql_snippet="SELECT 1;")],
        recommendations=[],
        risks=[],
        risk_score="LOW",
    )

    console = Mock()
    render_plan(plan, console)

    # Verify calls (simplified)
    assert console.print.called
