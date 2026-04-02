from typing import List

from .config import BackfillConfig, Dialect, Strategy
from .estimator import optimal_batch_size, estimate_phase_time, num_batches, total_time_estimate
from .plan import Plan, Phase


class BackfillPlanner:
    """
    Core planner: generates executable migration plan from config.
    """

    def __init__(self, config: BackfillConfig):
        self.config = config

    def _validate_constraints(self) -> List[str]:
        warnings = []
        total_sec, _ = total_time_estimate(self.config)
        if self.config.max_runtime_hours and total_sec / 3600 > self.config.max_runtime_hours:
            warnings.append("Est. time exceeds max_runtime_hours; increase throughput or filter rows")
        if self.config.total_rows > 1e9:
            warnings.append("Extremely large table; consider sharding or sampling")
        return warnings

    def _online_batched_phase(self) -> Phase:
        batch_size = optimal_batch_size(self.config)
        batches = num_batches(self.config.total_rows, batch_size)
        est_sec = estimate_phase_time(self.config.total_rows, self.config.write_throughput_avg)
        est_h = est_sec / 3600

        where = f"WHERE {self.config.where_clause}" if self.config.where_clause else ""
        col = self.config.column or "new_column"
        snippet = f"""UPDATE {self.config.table} 
SET {col} = 'migrated' 
{where} 
ORDER BY id  -- critical for consistency
LIMIT {batch_size} OFFSET %%%d;"""

        return Phase(
            name="Batched Updates",
            description="Incremental updates with LIMIT/OFFSET",
            est_duration_hours=est_h,
            batches=batches,
            sql_snippet=snippet,
            risks=["Repeated table scans if no ORDER BY index", "Long tail on uneven data"]
        )

    def _table_copy_phases(self) -> List[Phase):
        # Simplified CTAS
        copy_batch_size = optimal_batch_size(self.config)
        batches = num_batches(self.config.total_rows, copy_batch_size)
        copy_time_sec = estimate_phase_time(self.config.total_rows * 1.1, self.config.write_throughput_avg * 0.8)  # 10% overhead, slower
        copy_h = copy_time_sec / 3600

        return [
            Phase(
                name="CTAS New Table",
                description="CREATE TABLE AS SELECT with new column",
                est_duration_hours=copy_h,
                batches=1,
                sql_snippet=f"""CREATE TABLE {self.config.table}_new AS 
SELECT *, 'migrated' AS {self.config.column or 'status'} FROM {self.config.table};"""
            ),
            Phase(name="Atomic Swap", description="RENAME + indexes", est_duration_hours=0.02, batches=1,
                  sql_snippet="""ALTER TABLE ... RENAME TO old; RENAME new TO table; DROP old;"""),
        ]

    def generate_plan(self) -> Plan:
        warnings = self._validate_constraints()
        total_sec, batch_size = total_time_estimate(self.config)
        total_h = total_sec / 3600

        phases: List[Phase] = []
        if self.config.strategy == Strategy.ONLINE_BATCHED:
            phases = [self._online_batched_phase()]
        elif self.config.strategy == Strategy.TABLE_COPY:
            phases = self._table_copy_phases()

        # Add overhead phases
        phases = [
            Phase(name="Pre-flight Checks", description="ANALYZE/VACUUM", est_duration_hours=0.01, batches=1,
                  sql_snippet="ANALYZE " + self.config.table + ";"),
        ] + phases + [
            Phase(name="Post Verification", description="COUNT(*) checks", est_duration_hours=0.01, batches=1,
                  sql_snippet="SELECT COUNT(*) FROM " + self.config.table + " WHERE status IS NULL;"),
        ]

        risk_score = "LOW" if total_h < 1 else "MEDIUM" if total_h < 24 else "HIGH"

        return Plan(
            strategy=self.config.strategy.value,
            dialect=self.config.dialect.value,
            total_rows=self.config.total_rows,
            total_est_time_hours=round(total_h, 2),
            optimal_batch_size=batch_size,
            phases=phases,
            recommendations=[
                "Test on staging with 10% sample",
                f"Monitor at {batch_size // 1000}K row checkpoints",
                "Use connection pooling for high TPS",
            ],
            risks=warnings,
            risk_score=risk_score,
        )
