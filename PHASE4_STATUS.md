# SkillBridge — Phase 4: Course–Market Gap Analyzer

Implemented on top of the Phase 3 project.

## Added
- `backend/course_gap.py`: deterministic course-to-market comparison engine
- `GET /api/courses/{course_id}/market-roles`: ranks compatible market roles
- `GET /api/courses/{course_id}/gap`: returns alignment, matched/missing skills, action, recommendations and evidence
- `frontend/src/components/CourseGapAnalyzer.jsx`: focused course gap UI
- course `canonical_sector` mappings for the six MVP sectors
- focused UI helper styles
- `backend/test_course_gap.py`

## Decision logic
The score is calculated in Python from weighted role requirements and qualitative demand factors. The LLM is not involved.

Actions:
- `RETAIN`: >= 80% alignment
- `EXPAND`: 55–79.9%
- `UPDATE`: < 55%
- `REDUCE`: obsolete course, or high oversupply risk with low alignment

## Validation
- Python syntax checks: passed
- Course-gap tests: passed
- Catalog validation: 0 errors
- Catalog warnings remain for legacy course skills not represented in the 50-skill market catalog. They are intentionally not mass-added just to silence warnings.

## Frontend note
A full Vite build was not completed in this environment because dependency installation/native tooling was unavailable or timed out. The new component and client changes are self-contained.
