"""
Phase 1 catalog integrity checks. Run from backend/: python validate_catalog.py
"""

from __future__ import annotations

import sys
from collections import defaultdict

from catalog_models import CANONICAL_SECTORS, MAHARASHTRA_DISTRICTS
from data_store import load_courses, load_demand_signals, load_roles, load_skills

FORBIDDEN_SOURCE = "employer_feedback"


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    skills = load_skills()
    roles = load_roles()
    signals = load_demand_signals()
    courses = load_courses()

    skill_by_id = {s.id: s for s in skills}
    role_by_id = {r.id: r for r in roles}

    if len(skill_by_id) != len(skills):
        errors.append("duplicate skill id")
    names = [s.canonical_name.casefold() for s in skills]
    if len(names) != len(set(names)):
        errors.append("duplicate canonical skill names")

    alias_owner: dict[str, str] = {}
    canonical_keys = {s.canonical_name.casefold(): s.id for s in skills}
    for s in skills:
        for alias in s.aliases:
            key = alias.casefold()
            if key == s.canonical_name.casefold():
                continue
            if key in canonical_keys and canonical_keys[key] != s.id:
                errors.append(
                    f"alias '{alias}' on {s.id} collides with canonical name of {canonical_keys[key]}"
                )
            if key in alias_owner and alias_owner[key] != s.id:
                errors.append(
                    f"inconsistent alias '{alias}': {alias_owner[key]} and {s.id}"
                )
            alias_owner[key] = s.id

    sectors_from_skills = {s.sector for s in skills}
    missing_sectors = set(CANONICAL_SECTORS) - sectors_from_skills
    if missing_sectors:
        errors.append(f"skills catalog missing sectors: {sorted(missing_sectors)}")

    roles_by_sector: dict[str, int] = defaultdict(int)
    for role in roles:
        roles_by_sector[role.sector] += 1
        seen = set()
        for req in role.required_skills:
            if req.skill_id not in skill_by_id:
                errors.append(f"{role.id} references unknown skill {req.skill_id}")
            elif req.skill_id in seen:
                errors.append(f"{role.id} duplicate required skill {req.skill_id}")
            seen.add(req.skill_id)
        for loc in role.typical_locations:
            if loc not in MAHARASHTRA_DISTRICTS and loc != "Maharashtra":
                errors.append(f"{role.id} location not in demo district list: {loc}")
    for sector in CANONICAL_SECTORS:
        if roles_by_sector[sector] < 1:
            errors.append(f"no role for sector {sector}")

    signal_ids = [s.id for s in signals]
    if len(signal_ids) != len(set(signal_ids)):
        errors.append("duplicate demand signal id")

    covered: set[tuple[str, str]] = set()
    for sig in signals:
        if sig.source_type == FORBIDDEN_SOURCE:
            errors.append(f"{sig.id} fabricates employer_feedback")
        if sig.role_id not in role_by_id:
            errors.append(f"{sig.id} unknown role_id {sig.role_id}")
            continue
        if sig.skill_id not in skill_by_id:
            errors.append(f"{sig.id} unknown skill_id {sig.skill_id}")
            continue
        role = role_by_id[sig.role_id]
        if sig.sector != role.sector:
            errors.append(f"{sig.id} sector {sig.sector} != role sector {role.sector}")
        role_skill_ids = {r.skill_id for r in role.required_skills}
        if sig.skill_id not in role_skill_ids:
            errors.append(f"{sig.id} skill {sig.skill_id} not on {sig.role_id}")
        if not sig.source or not sig.evidence:
            errors.append(f"{sig.id} missing source or evidence")
        if sig.data_status != "demo":
            errors.append(f"{sig.id} data_status must be demo")
        covered.add((sig.role_id, sig.skill_id))

    for role in roles:
        for req in role.required_skills:
            if (role.id, req.skill_id) not in covered:
                errors.append(f"no demand signal for {role.id} / {req.skill_id}")

    course_ids = [c.id for c in courses]
    if len(course_ids) != len(set(course_ids)):
        errors.append("duplicate course id")

    mapped = 0
    for course in courses:
        if course.district not in MAHARASHTRA_DISTRICTS:
            errors.append(f"{course.id} district '{course.district}' not in Maharashtra demo list")
        if course.canonical_sector:
            mapped += 1
        for raw in course.skills_taught:
            key = raw.casefold()
            hit = key in alias_owner or key in canonical_keys
            if not hit:
                # substring against aliases for multi-skill course strings
                hit = any(
                    key in a.casefold() or a.casefold() in key
                    for a in list(alias_owner) + list(canonical_keys)
                )
            if not hit:
                warnings.append(f"{course.id} skill not in catalog aliases: {raw}")

    if mapped < 6:
        errors.append("expected courses mapped into the six canonical sectors")

    print(f"skills={len(skills)} roles={len(roles)} signals={len(signals)} courses={len(courses)}")
    print(f"warnings={len(warnings)} errors={len(errors)}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
