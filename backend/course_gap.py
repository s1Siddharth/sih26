"""Deterministic course-to-market gap analysis for SkillBridge."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from catalog_models import CourseRecord, DemandSignalRecord, RoleRecord, SkillRecord


@dataclass(frozen=True)
class SkillIndex:
    canonical_to_id: dict[str, str]
    alias_to_id: dict[str, str]
    id_to_name: dict[str, str]


def _key(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def build_skill_index(skills: list[SkillRecord]) -> SkillIndex:
    canonical_to_id: dict[str, str] = {}
    alias_to_id: dict[str, str] = {}
    id_to_name: dict[str, str] = {}
    for skill in skills:
        canonical_to_id[_key(skill.canonical_name)] = skill.id
        id_to_name[skill.id] = skill.canonical_name
    for skill in skills:
        for alias in skill.aliases:
            alias_to_id[_key(alias)] = skill.id
    return SkillIndex(canonical_to_id, alias_to_id, id_to_name)


def resolve_skill(value: str, index: SkillIndex) -> str | None:
    k = _key(value)
    if k in index.canonical_to_id:
        return index.canonical_to_id[k]
    if k in index.alias_to_id:
        return index.alias_to_id[k]
    return None


def _demand_factor(level: str) -> float:
    return {"high": 1.0, "medium": 0.75, "low": 0.5}.get(level, 0.75)


def analyze_course(
    course: CourseRecord,
    role: RoleRecord,
    skills: list[SkillRecord],
    signals: list[DemandSignalRecord],
) -> dict[str, Any]:
    index = build_skill_index(skills)
    taught_ids = {sid for raw in course.skills_taught if (sid := resolve_skill(raw, index))}

    relevant_signals = [
        s for s in signals
        if s.role_id == role.id and (s.location in course.district, s.location == "Maharashtra")
    ]
    signal_by_skill: dict[str, list[DemandSignalRecord]] = defaultdict(list)
    for signal in relevant_signals:
        signal_by_skill[signal.skill_id].append(signal)

    rows = []
    total_weight = 0.0
    matched_weight = 0.0
    missing_weight = 0.0
    weak_weight = 0.0

    for req in role.required_skills:
        demand = max((signal.demand_level for signal in signal_by_skill.get(req.skill_id, [])), key=lambda x: _demand_factor(x), default="medium")
        effective_weight = req.weight * _demand_factor(demand)
        total_weight += effective_weight
        taught = req.skill_id in taught_ids
        status = "matched" if taught else "missing"
        if taught:
            matched_weight += effective_weight
        else:
            missing_weight += effective_weight
        rows.append({
            "skill_id": req.skill_id,
            "skill": index.id_to_name.get(req.skill_id, req.skill_id),
            "status": status,
            "required_proficiency": req.proficiency,
            "demand_level": demand,
            "weight": req.weight,
        })

    score = round((matched_weight / total_weight * 100) if total_weight else 0.0, 1)
    missing = [r for r in rows if r["status"] == "missing"]
    matched = [r for r in rows if r["status"] == "matched"]

    if course.is_obsolete or (course.oversupply_risk == "high" and score < 60):
        action = "REDUCE"
        priority = "high"
    elif score >= 80:
        action = "RETAIN"
        priority = "low"
    elif score >= 55:
        action = "EXPAND"
        priority = "medium"
    else:
        action = "UPDATE"
        priority = "high"

    recommendations = []
    for item in sorted(missing, key=lambda r: (-r["weight"], r["skill"]))[:5]:
        recommendations.append(
            f"Add or strengthen {item['skill']} ({item['demand_level']} market demand) in the {course.trade_name} curriculum."
        )
    if not recommendations:
        recommendations.append("Maintain the current curriculum and review market signals periodically.")

    evidence = []
    for item in rows:
        for signal in signal_by_skill.get(item["skill_id"], []):
            evidence.append({
                "skill": item["skill"],
                "demand_level": signal.demand_level,
                "source_type": signal.source_type,
                "source": signal.source,
                "source_date": signal.source_date.isoformat(),
                "evidence": signal.evidence,
            })

    return {
        "course": {"id": course.id, "trade_name": course.trade_name, "district": course.district, "sector": course.canonical_sector or course.sector},
        "target_role": {"id": role.id, "name": role.name, "sector": role.sector},
        "alignment_score": score,
        "score_breakdown": {
            "matched_weight": round(matched_weight, 2),
            "required_weight": round(total_weight, 2),
            "skill_coverage_percent": score,
        },
        "matched_skills": [r["skill"] for r in matched],
        "missing_skills": [r["skill"] for r in missing],
        "skill_comparison": rows,
        "recommended_action": action,
        "priority": priority,
        "recommendations": recommendations,
        "evidence": evidence,
        "data_status": "demo",
    }


def rank_roles_for_course(course: CourseRecord, roles: list[RoleRecord], skills: list[SkillRecord], signals: list[DemandSignalRecord]) -> list[dict[str, Any]]:
    sector = course.canonical_sector
    candidates = [r for r in roles if not sector or r.sector == sector]
    results = []
    for role in candidates:
        report = analyze_course(course, role, skills, signals)
        results.append({"role_id": role.id, "role": role.name, "sector": role.sector, "alignment_score": report["alignment_score"]})
    return sorted(results, key=lambda x: (-x["alignment_score"], x["role"]))
