import pytest
from backfill_planner.config import BackfillConfig, Strategy
from backfill_planner.planner import BackfillPlanner


def test_planner_generates_plan(sample_config_dict):
    config = BackfillConfig(**sample_config_dict)
    planner = BackfillPlanner(config)
    plan = planner.generate_plan()
    assert plan.total_rows == 1000000
    assert len(plan.phases) >= 3
    assert plan.total_est_time_hours > 0
    assert "UPDATE" in plan.phases[1].sql_snippet


def test_table_copy_strategy(sample_config_dict):
    config_dict = sample_config_dict.copy()
    config_dict["strategy"] = "table-copy"
    config = BackfillConfig(**config_dict)
    planner = BackfillPlanner(config)
    plan = planner.generate_plan()
    assert any("CTAS" in p.name for p in plan.phases)


def test_max_runtime_warning(sample_config_dict):
    config_dict = sample_config_dict.copy()
    config_dict["total_rows"] = 100000000
    config_dict["write_throughput_avg"] = 10.0
    config_dict["max_runtime_hours"] = 1.0
    config = BackfillConfig(**config_dict)
    planner = BackfillPlanner(config)
    plan = planner.generate_plan()
    assert any("exceeds max_runtime_hours" in r for r in plan.risks)
