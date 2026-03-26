from typing import Dict, Any, List
from datetime import datetime, timedelta

SECURITY_CHECKS = {
    "strict-transport-security": 20,
    "content-security-policy": 15,
    "content-security-policy-report-only": 10,
    "x-frame-options": 10,
    "x-content-type-options": 10,
    "referrer-policy": 5,
    "permissions-policy": 5,
    "x-xss-protection": 5,
}


def get_security_score(headers: Dict[str, str], ssl_info: Dict[str, Any]) -> Dict[str, Any]:
    """Compute security score and issues."""
    score = 100
    issues: List[str] = []
    recommendations = []

    lower_headers = {k.lower(): v for k, v in headers.items()}

    for header, points in SECURITY_CHECKS.items():
        if header not in lower_headers:
            score -= points
            issues.append(f"Missing {header.replace('-', ' ').title()}")
            recommendations.append(f"Add {header}")

    # SSL expiry
    if "error" not in ssl_info:
        try:
            expiry_str = ssl_info["not_after"]
            expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if expiry < datetime.now(tz=expiry.tzinfo) + timedelta(days=30):
                score -= 25
                issues.append("SSL certificate expiring soon")
                recommendations.append("Renew SSL certificate")
        except:
            pass

    # CORS any
    if "access-control-allow-origin" in lower_headers and lower_headers["access-control-allow-origin"] == "*":
        score -= 10
        issues.append("CORS allows all origins (*)")
        recommendations.append("Restrict CORS origins")

    return {
        "score": max(0, score),
        "issues": issues,
        "recommendations": recommendations,
    }