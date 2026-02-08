import json
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup
from dataclasses import dataclass
from requests import Session, RequestException
from urllib.parse import urljoin, urlparse

from .schemas import MANIFEST_VALIDATOR
from .output import CheckResult


@dataclass
class PWAAuditor:
    url: str
    timeout: float = 10.0
    session: Session = None
    base_url: str = ""
    html_soup: Optional[BeautifulSoup] = None

    def __post_init__(self) -> None:
        self.parsed_url = urlparse(self.url)
        self.base_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        self.session = Session()
        self.session.headers.update({"User-Agent": "PWA-Auditor-CLI/0.1.0"})

    def fetch(self, url: str) -> Optional[dict]:
        """Fetch URL and return response or None on error."""
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()
            return resp
        except RequestException as e:
            return None

    def run_checks(self) -> List[CheckResult]:
        results: List[CheckResult] = []

        # Site reachability
        html_resp = self.fetch(self.url)
        if not html_resp:
            details = f"Failed to fetch {self.url}"
            results.append(CheckResult("Site Reachability", False, details, 0, 10))
            return results
        self.html_soup = BeautifulSoup(html_resp.text, "lxml")
        results.append(CheckResult("Site Reachability", True, "OK", 10, 10))

        # HTTPS
        results.append(self._https_check())

        # Manifest
        manifest_result = self._manifest_check()
        results.extend([manifest_result, self._manifest_schema_check(manifest_result)])

        # Service Worker
        results.append(self._service_worker_check())

        # Viewport
        results.append(self._viewport_check())

        # Theme Color
        results.append(self._theme_color_check())

        # Apple PWA metas
        results.append(self._apple_pwa_check())

        return results

    def _https_check(self) -> CheckResult:
        passed = self.parsed_url.scheme == "https"
        details = "OK" if passed else "PWA requires HTTPS"
        points = 20 if passed else 0
        return CheckResult("HTTPS", passed, details, points, 20)

    def _manifest_check(self) -> CheckResult:
        if not self.html_soup:
            return CheckResult("Manifest Present", False, "No HTML", 0, 10)
        manifest_link = self.html_soup.find("link", {"rel": "manifest"})
        if not manifest_link or "href" not in manifest_link.attrs:
            return CheckResult("Manifest Present", False, "No <link rel=\"manifest\" href=...>", 0, 10)
        manifest_url = urljoin(self.base_url, manifest_link["href"])
        resp = self.fetch(manifest_url)
        if not resp:
            return CheckResult("Manifest Fetchable", False, f"Failed to fetch {manifest_url}", 0, 10)
        try:
            manifest = resp.json()
            self._cached_manifest = manifest  # Cache for schema check
            return CheckResult("Manifest Fetchable", True, manifest_url, 10, 10)
        except json.JSONDecodeError:
            return CheckResult("Manifest Fetchable", False, "Invalid JSON", 0, 10)

    def _manifest_schema_check(self, manifest_check: CheckResult) -> CheckResult:
        if not hasattr(self, "_cached_manifest"):
            return CheckResult("Manifest Schema", False, "No manifest", 0, 15)
        try:
            MANIFEST_VALIDATOR.validate(self._cached_manifest)
            # Bonus for good icons (192/512)
            icons = self._cached_manifest.get("icons", [])
            good_sizes = any("192x192" in icon.get("sizes", "") or "512x512" in icon.get("sizes", "") for icon in icons)
            details = "Valid (good icons)" if good_sizes else "Valid"
            return CheckResult("Manifest Schema", True, details, 15, 15)
        except Exception as e:
            return CheckResult("Manifest Schema", False, f"Invalid: {str(e)[:100]}", 0, 15)

    def _service_worker_check(self) -> CheckResult:
        candidates = ["/sw.js", "/service-worker.js", "/worker.js"]
        for path in candidates:
            sw_url = urljoin(self.base_url, path)
            resp = self.fetch(sw_url)
            if resp and resp.status_code == 200 and "javascript" in resp.headers.get("content-type", ""):
                return CheckResult("Service Worker", True, f"Found: {path}", 15, 15)
        # Fallback: search HTML
        if self.html_soup and "serviceWorker.register" in self.html_soup.get_text():
            return CheckResult("Service Worker", True, "JS registration found in HTML", 10, 15)
        return CheckResult("Service Worker", False, "No SW file or registration", 0, 15)

    def _viewport_check(self) -> CheckResult:
        if not self.html_soup:
            return CheckResult("Viewport", False, "No HTML", 0, 5)
        viewport = self.html_soup.find("meta", {"name": "viewport"})
        if viewport and "width=device-width" in viewport.get("content", ""):
            return CheckResult("Viewport", True, "OK", 5, 5)
        return CheckResult("Viewport", False, "Missing/invalid viewport meta", 0, 5)

    def _theme_color_check(self) -> CheckResult:
        if not self.html_soup:
            return CheckResult("Theme Color", False, "No HTML", 0, 5)
        theme = self.html_soup.find("meta", {"name": "theme-color"})
        if theme and theme.get("content"):
            return CheckResult("Theme Color", True, theme["content"], 5, 5)
        return CheckResult("Theme Color", False, "Missing theme-color meta", 0, 5)

    def _apple_pwa_check(self) -> CheckResult:
        if not self.html_soup:
            return CheckResult("Apple PWA", False, "No HTML", 0, 10)
        capable = self.html_soup.find("meta", {"name": "apple-mobile-web-app-capable", "content": "yes"})
        status_bar = self.html_soup.find("meta", {"name": "apple-mobile-web-app-status-bar-style"})
        touch_icon = self.html_soup.find("link", {"rel": "apple-touch-icon"})
        passed = bool(capable and (status_bar or touch_icon))
        points = 10 if passed else (5 if any([capable, status_bar, touch_icon]) else 0)
        details = "Full support" if passed else "Partial/missing metas"
        return CheckResult("Apple PWA", passed, details, points, 10)
