import pytest
from pathlib import Path

from monorepo_dep_aligner.auditor import audit_deps
from monorepo_dep_aligner.parser import parse_package_deps, find_pyprojects
from monorepo_dep_aligner.types import PackageInfo


class TestAuditDeps:
    @pytest.fixture
    def packages(self, conflict_monorepo: Path) -> list[PackageInfo]:
        pyprojects = find_pyprojects(conflict_monorepo)
        return [
            {"path": p, "deps": parse_package_deps(p)}  # type: ignore
            for p in pyprojects
            if parse_package_deps(p)
        ]

    def test_conflicts(self, packages: list[PackageInfo]):
        conflicts = audit_deps(packages)
        assert "requests" in conflicts
        assert len(conflicts["requests"]) == 2

    def test_no_conflicts(self):
        pkgs = [
            {"path": Path("a"), "deps": {"foo": ["1.0"]}},
            {"path": Path("b"), "deps": {"foo": ["1.0"]}},
        ]
        assert audit_deps(pkgs) == {}

    def test_multi_specs_per_pkg(self):
        pkgs = [
            {
                "path": Path("a"),
                "deps": {"foo": ["^1.0", ">=1.0"]},
            },
        ]
        conflicts = audit_deps(pkgs)
        assert "foo" in conflicts  # Detects even within pkg