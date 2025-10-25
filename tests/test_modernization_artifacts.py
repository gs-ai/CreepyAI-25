import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs" / "modernization_plan.md"
DEPENDENCY_PATH = ROOT / "docs" / "dependency_inventory.csv"
CONDA_PATH = ROOT / "environments" / "conda-env.yaml"


@pytest.mark.parametrize(
    "path",
    [PLAN_PATH, DEPENDENCY_PATH, CONDA_PATH, ROOT / "docker" / "Dockerfile.dev"],
)
def test_artifact_exists(path: Path) -> None:
    assert path.exists(), f"Expected artifact missing: {path}"


def test_dependency_inventory_has_required_columns() -> None:
    with DEPENDENCY_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        expected = [
            "package",
            "current_version",
            "recommended_version",
            "justification",
            "risk_level",
        ]
        assert reader.fieldnames == expected, "CSV header does not match required columns"
        rows = list(reader)
        assert rows, "Dependency inventory must not be empty"
        for row in rows:
            for key in expected:
                assert row[key] != "", f"Missing value for {key} in {row['package']}"


def test_modernization_plan_sections_present() -> None:
    content = PLAN_PATH.read_text(encoding="utf-8")
    required_sections = [
        "Objective Alignment",
        "Current System Inventory",
        "Module Classification",
        "Migration Phases",
        "Environment Provisioning",
        "CI/CD Blueprint",
        "Verification Checklist",
        "Repo Restructuring Plan",
        "TODO Roadmap",
        "Acceptance Criteria",
    ]
    for section in required_sections:
        assert f"## {section}" in content, f"Section '{section}' missing from modernization plan"
