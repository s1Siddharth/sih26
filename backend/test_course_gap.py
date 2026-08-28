from data_store import load_courses, load_demand_signals, load_roles, load_skills
from course_gap import analyze_course, build_skill_index, rank_roles_for_course, resolve_skill

skills = load_skills(); roles = load_roles(); signals = load_demand_signals(); courses = load_courses()
idx = build_skill_index(skills)
assert resolve_skill('PLC programming basics', idx) == 'sk_plc_programming'
assert resolve_skill('not-a-real-skill', idx) is None

course = next(c for c in courses if c.id == 'NSDC-002')
role = next(r for r in roles if r.id == 'role_automation_technician')
report = analyze_course(course, role, skills, signals)
assert 0 <= report['alignment_score'] <= 100
assert report['recommended_action'] in {'UPDATE','EXPAND','REDUCE','RETAIN'}
assert report['score_breakdown']['skill_coverage_percent'] == report['alignment_score']

for c in courses:
    ranked = rank_roles_for_course(c, roles, skills, signals)
    if ranked:
        assert ranked == sorted(ranked, key=lambda x: (-x['alignment_score'], x['role']))
print('course gap tests: PASS')
