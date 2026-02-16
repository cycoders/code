import logging
from typing import Dict, Any
from .types import LighthouseResult, Metric

logger = logging.getLogger(__name__)

VITAL_AUDITS = {
    "largest-contentful-paint": "lcp",
    "interaction-to-next-paint": "inp",
    "cumulative-layout-shift": "cls",
    "first-contentful-paint": "fcp",
    "server-response-time": "ttfb",
}


def parse_lighthouse_json(data: Dict[str, Any]) -> LighthouseResult:
    """Parse Lighthouse JSON to structured result."""
    categories = data.get("categories", {})
    perf_category = categories.get("performance", {})

    metrics = {}
    audits = data.get("audits", {})
    for audit_id, vital_key in VITAL_AUDITS.items():
        audit = audits.get(audit_id, {})
        metrics[vital_key] = Metric(
            displayValue=audit.get("displayValue", "N/A"),
            numericValue=audit.get("numericValue", 0.0),
            score=audit.get("score"),
            details=audit.get("details"),
        )

    return LighthouseResult(
        score=perf_category.get("score", 0.0),
        metrics=metrics,
        audits=audits,
        categories=categories,
    )