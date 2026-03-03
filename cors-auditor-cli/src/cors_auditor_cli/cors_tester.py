import httpx
from typing import List
from rich.progress import Progress

from .models import AuditConfig, AuditReport, CheckResult, TestCase

class CorsTester:
    def __init__(self, config: AuditConfig):
        self.config = config
        self.client = httpx.Client(
            timeout=config.timeout, follow_redirects=True, verify=True
        )

    def run(self) -> AuditReport:
        report = AuditReport(url=self.config.url, checks=[])
        test_cases: List[TestCase] = []

        with Progress() as progress:
            task = progress.add_task("[green]Auditing CORS...", total=len(self.config.origins))

            for origin in self.config.origins:
                test_case = TestCase(origin=origin)

                # Simple request
                simple_result = self._do_simple_request(origin)
                test_case.simple_request = simple_result
                report.checks.append(simple_result)

                # Preflight
                preflight_result = self._do_preflight_request(origin)
                test_case.preflight_request = preflight_result
                report.checks.append(preflight_result)

                test_cases.append(test_case)
                progress.advance(task)

        report.test_cases = test_cases
        report._compute_summary()
        return report

    def _do_simple_request(self, origin: str) -> CheckResult:
        headers = {"Origin": origin}
        if self.config.credentials:
            headers["Cookie"] = "test=1"  # Trigger credentials mode

        resp = self.client.get(self.config.url, headers=headers)

        acao = resp.headers.get("access-control-allow-origin", "")
        acac = resp.headers.get("access-control-allow-credentials", "")
        vary = resp.headers.get("vary", "")

        checks = []
        passed = True

        # ACAO check
        if origin == acao or acao == "*":
            checks.append("ACAO matches origin or wildcard")
        else:
            checks.append("❌ ACAO mismatch")
            passed = False

        # Credentials
        if self.config.credentials:
            if acao == "*":
                checks.append("❌ Wildcard ACAO with credentials")
                passed = False
            if acac != "true":
                checks.append("❌ ACAC not 'true' for credentials")
                passed = False
        
        if "Origin" not in vary:
            checks.append("⚠ Missing Vary: Origin")

        return CheckResult(
            type="simple",
            origin=origin,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            passed=passed,
            details=checks,
        )

    def _do_preflight_request(self, origin: str) -> CheckResult:
        acr_headers = ", ".join(self.config.request_headers)
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": self.config.methods[0],
            "Access-Control-Request-Headers": acr_headers,
        }

        resp = self.client.options(self.config.url, headers=headers)

        acao = resp.headers.get("access-control-allow-origin", "")
        acam = resp.headers.get("access-control-allow-methods", "")
        acah = resp.headers.get("access-control-allow-headers", "")
        acac = resp.headers.get("access-control-allow-credentials", "")
        max_age = resp.headers.get("access-control-max-age", "")

        checks = []
        passed = True

        # ACAO
        if origin != acao:
            checks.append("❌ Preflight ACAO mismatch")
            passed = False

        # ACAM
        for method in self.config.methods:
            if method not in acam.split(","):
                checks.append(f"❌ Method {method} not allowed")
                passed = False

        # ACAH
        for rh in self.config.request_headers:
            if rh.lower() not in [h.strip().lower() for h in acah.split(",")]:
                checks.append(f"❌ Header '{rh}' not allowed")
                passed = False

        # ACAC
        if self.config.credentials and acac != "true":
            checks.append("❌ Preflight ACAC not 'true'")
            passed = False

        if not max_age.isdigit():
            checks.append("⚠ Invalid or missing max-age")

        return CheckResult(
            type="preflight",
            origin=origin,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            passed=passed,
            details=checks,
        )