"""Deterministic resume-to-market alignment for SkillBridge."""
from __future__ import annotations

from typing import Any
from course_gap import build_skill_index, resolve_skill, _demand_factor
from catalog_models import RoleRecord, SkillRecord, DemandSignalRecord
from models import ParsedResume


def _norm(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _contains_any(values: list[str], text: str) -> bool:
    blob = _norm(" ".join(values))
    return any(_norm(v) in blob for v in values if v)


def _role_score(resume: ParsedResume, role: RoleRecord, skills: list[SkillRecord]) -> float:
    idx = build_skill_index(skills)
    resume_ids = {resolve_skill(s, idx) for s in resume.skills}
    resume_ids.discard(None)
    if not role.required_skills:
        return 0.0
    total = sum(r.weight for r in role.required_skills)
    matched = sum(r.weight for r in role.required_skills if r.skill_id in resume_ids)
    return round((matched / total) * 100, 1) if total else 0.0


def rank_roles(resume: ParsedResume, roles: list[RoleRecord], skills: list[SkillRecord], limit: int = 5) -> list[dict[str, Any]]:
    results = []
    for role in roles:
        results.append({
            "role_id": role.id,
            "role": role.name,
            "sector": role.sector,
            "alignment_score": _role_score(resume, role, skills),
        })
    return sorted(results, key=lambda x: (-x["alignment_score"], x["role"]))[:limit]


def analyze_resume(
    resume: ParsedResume,
    role: RoleRecord,
    skills: list[SkillRecord],
    signals: list[DemandSignalRecord],
) -> dict[str, Any]:
    idx = build_skill_index(skills)
    resume_ids = {resolve_skill(s, idx) for s in resume.skills}
    resume_ids.discard(None)

    role_signals = [s for s in signals if s.role_id == role.id]
    signal_by_skill = {}
    for signal in role_signals:
        signal_by_skill.setdefault(signal.skill_id, []).append(signal)

    rows = []
    required_weight = matched_weight = 0.0
    for req in role.required_skills:
        signals_for_skill = signal_by_skill.get(req.skill_id, [])
        demand = max((s.demand_level for s in signals_for_skill), key=_demand_factor, default="medium")
        effective_weight = req.weight * _demand_factor(demand)
        matched = req.skill_id in resume_ids
        required_weight += effective_weight
        if matched:
            matched_weight += effective_weight
        rows.append({
            "skill_id": req.skill_id,
            "skill": idx.id_to_name.get(req.skill_id, req.skill_id),
            "status": "matched" if matched else "gap",
            "required_proficiency": req.proficiency,
            "demand_level": demand,
            "weight": req.weight,
        })

    skill_score = (matched_weight / required_weight * 100) if required_weight else 0.0
    matched = [r for r in rows if r["status"] == "matched"]
    gaps = [r for r in rows if r["status"] == "gap"]

    experience_signal = 100.0 if resume.experiences or (resume.total_experience_years or 0) > 0 else 0.0
    project_signal = 100.0 if resume.projects else 0.0
    support_score = (experience_signal * 0.6) + (project_signal * 0.4)
    final_score = round((skill_score * 0.9) + (support_score * 0.1), 1)

    recommendations = []
    for item in sorted(gaps, key=lambda r: (-r["weight"] * _demand_factor(r["demand_level"]), r["skill"]))[:5]:
        recommendations.append(
            f"Build a practical project or training module covering {item['skill']} because it is a {item['demand_level']}-demand requirement for {role.name}."
        )
    if not resume.projects and len(recommendations) < 5:
        recommendations.append(f"Add one project demonstrating the core skills required for {role.name}.")
    if not resume.experiences and len(recommendations) < 5:
        recommendations.append("Add internship, apprenticeship, or hands-on experience evidence where available.")
    recommendations = recommendations[:5]

    evidence = []
    seen = set()
    for item in gaps + matched:
        for signal in signal_by_skill.get(item["skill_id"], []):
            key = (signal.id, item["skill_id"])
            if key in seen:
                continue
            seen.add(key)
            evidence.append({
                "skill": item["skill"],
                "demand_level": signal.demand_level,
                "source_type": signal.source_type,
                "source": signal.source,
                "source_date": signal.source_date.isoformat(),
                "evidence": signal.evidence,
            })

    return {
        "alignment_score": final_score,
        "target_role": {"id": role.id, "name": role.name, "sector": role.sector},
        "matched_skills": [r["skill"] for r in matched],
        "missing_skills": [r["skill"] for r in gaps],
        "score_breakdown": {
            "skill_coverage": round(skill_score, 1),
            "experience_evidence": round(experience_signal, 1),
            "project_evidence": round(project_signal, 1),
            "final_score": final_score,
        },
        "skill_comparison": rows,
        "recommendations": recommendations,
        "evidence": evidence,
        "data_status": "demo",
    }
