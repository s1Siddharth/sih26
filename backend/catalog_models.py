"""
Canonical labour-market records (table-shaped for a later SQLite swap).

JSON files are the store. IDs are stable primary keys. Foreign keys are
skill_id / role_id strings. Matching/scoring must import these models,
not invent parallel schemas.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# --- Controlled vocabularies (SQLite CHECK constraints later) ---

Sector = Literal[
    "IT / Digital",
    "Manufacturing",
    "Automotive / EV",
    "Healthcare",
    "Logistics",
    "Renewable Energy",
]

DemandLevel = Literal["high", "medium", "low"]
SourceType = Literal[
    "job_posting",
    "industry_report",
    "employer_feedback",
    "government_data",
    "trend",
]
DataStatus = Literal["demo"]
Proficiency = Literal["basic", "intermediate", "advanced"]
OversupplyRisk = Literal["high", "medium", "low"]

CANONICAL_SECTORS: tuple[str, ...] = (
    "IT / Digital",
    "Manufacturing",
    "Automotive / EV",
    "Healthcare",
    "Logistics",
    "Renewable Energy",
)

MAHARASHTRA_DISTRICTS: tuple[str, ...] = (
    "Pune",
    "Mumbai",
    "Nagpur",
    "Nashik",
    "Thane",
    "Kolhapur",
    "Solapur",
    "Aurangabad",
)

MAHARASHTRA_LOCATIONS: tuple[str, ...] = MAHARASHTRA_DISTRICTS + ("Maharashtra",)


class CatalogMeta(BaseModel):
    """File-level metadata. Maps to a `meta` table later."""

    geography: Literal["Maharashtra"] = "Maharashtra"
    data_status: DataStatus = "demo"
    note: str = Field(
        default=(
            "Qualitative Maharashtra demo corpus for SIH26134. "
            "Not live vacancy counts or verified district-level statistics."
        )
    )


class SkillRecord(BaseModel):
    """One canonical skill. Table: skills."""

    id: str = Field(description="Primary key, e.g. sk_cnc_programming")
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    sector: Sector
    proficiency_levels: list[Proficiency] = Field(
        default_factory=lambda: ["basic", "intermediate", "advanced"]
    )

    @field_validator("id")
    @classmethod
    def id_prefix(cls, v: str) -> str:
        if not v.startswith("sk_"):
            raise ValueError("skill id must start with sk_")
        return v

    @field_validator("aliases")
    @classmethod
    def aliases_stripped(cls, v: list[str]) -> list[str]:
        cleaned = []
        seen = set()
        for a in v:
            item = a.strip()
            if not item:
                continue
            key = item.casefold()
            if key not in seen:
                seen.add(key)
                cleaned.append(item)
        return cleaned


class RoleSkillRequirement(BaseModel):
    """Role–skill junction. Table: role_skills."""

    skill_id: str
    weight: float = Field(ge=0.1, le=1.0, default=1.0)
    proficiency: Proficiency = "intermediate"


class RoleRecord(BaseModel):
    """Target occupation. Table: roles."""

    id: str
    name: str
    sector: Sector
    required_skills: list[RoleSkillRequirement]
    typical_locations: list[str] = Field(
        default_factory=list,
        description="Maharashtra districts used in demo course/institute data",
    )

    @field_validator("id")
    @classmethod
    def id_prefix(cls, v: str) -> str:
        if not v.startswith("role_"):
            raise ValueError("role id must start with role_")
        return v

    @field_validator("typical_locations")
    @classmethod
    def mh_locations(cls, v: list[str]) -> list[str]:
        bad = [loc for loc in v if loc not in MAHARASHTRA_LOCATIONS]
        if bad:
            raise ValueError(f"locations must be Maharashtra demo districts: {bad}")
        return v

    @field_validator("required_skills")
    @classmethod
    def unique_skill_ids(cls, v: list[RoleSkillRequirement]) -> list[RoleSkillRequirement]:
        ids = [r.skill_id for r in v]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate skill_id on role")
        if not v:
            raise ValueError("role must list at least one required skill")
        return v


class DemandSignalRecord(BaseModel):
    """
    One qualitative demand observation. Table: demand_signals.

    signal_score is a 1–5 demo ordinal for ranking inside this corpus.
    It is not a job-opening count and not a live statistic.
    """

    id: str
    sector: Sector
    role_id: str
    skill_id: str
    location: str
    demand_level: DemandLevel
    signal_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Demo ordinal 1–5 derived from source emphasis; not a vacancy count",
    )
    source_type: SourceType
    source: str
    source_date: date
    evidence: str
    data_status: DataStatus = "demo"

    @field_validator("id")
    @classmethod
    def id_prefix(cls, v: str) -> str:
        if not v.startswith("ds_"):
            raise ValueError("demand signal id must start with ds_")
        return v

    @field_validator("location")
    @classmethod
    def mh_location(cls, v: str) -> str:
        if v not in MAHARASHTRA_LOCATIONS:
            raise ValueError(f"location must be a Maharashtra demo location, got {v}")
        return v

    @field_validator("source", "evidence")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("source and evidence are required")
        return v.strip()

    @model_validator(mode="after")
    def no_live_claim(self) -> "DemandSignalRecord":
        blob = f"{self.source} {self.evidence}".casefold()
        if "live" in blob and "not live" not in blob:
            raise ValueError("do not claim live statistics in source/evidence")
        return self


class CourseRecord(BaseModel):
    """Existing course catalog row. Table: courses."""

    id: str
    trade_name: str
    program_type: str
    skills_taught: list[str]
    duration_months: int
    enrollment: int
    placement_rate: float
    institute: str
    district: str
    sector: str = Field(description="Legacy sector label on the original catalog")
    canonical_sector: Optional[Sector] = Field(
        default=None,
        description="Mapped MVP sector, or null if the course is outside the six sectors",
    )
    is_obsolete: bool = False
    oversupply_risk: OversupplyRisk = "low"
    last_curriculum_update: int


class SkillCatalogFile(BaseModel):
    meta: CatalogMeta
    skills: list[SkillRecord]


class RoleCatalogFile(BaseModel):
    meta: CatalogMeta
    roles: list[RoleRecord]


class DemandSignalFile(BaseModel):
    meta: CatalogMeta
    signals: list[DemandSignalRecord]
