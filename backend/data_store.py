"""
JSON-backed catalog access.
"""

from __future__ import annotations

import json
from pathlib import Path

from catalog_models import (
    CourseRecord,
    DemandSignalFile,
    DemandSignalRecord,
    RoleCatalogFile,
    RoleRecord,
    SkillCatalogFile,
    SkillRecord,
)

DATA_DIR = Path(__file__).parent / "data"


def _read_json(name: str) -> dict | list:
    path = DATA_DIR / name

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_skills() -> list[SkillRecord]:
    payload = SkillCatalogFile.model_validate(
        _read_json("skills_catalog.json")
    )
    return payload.skills


def load_roles() -> list[RoleRecord]:
    payload = RoleCatalogFile.model_validate(
        _read_json("roles.json")
    )
    return payload.roles


def load_demand_signals() -> list[DemandSignalRecord]:
    payload = DemandSignalFile.model_validate(
        _read_json("demand_signals.json")
    )
    return payload.signals


def load_courses() -> list[CourseRecord]:
    raw = _read_json("courses.json")

    return [
        CourseRecord.model_validate(row)
        for row in raw
    ]