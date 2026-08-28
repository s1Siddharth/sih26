"""
FastAPI backend for SkillBridge — Skill-Market Alignment Platform.
PS #26134: Challenges in aligning skill development programs with industry requirements.
"""

import json
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from models import (
    ExtractionRequest, ExtractedSkills,
    SkillGapReport, FeedbackRequest, FeedbackItem,
    ProgramRecommendation, SkillComparisonEntry,
)
from analysis import extract_skills_from_text, parse_job_postings_file
from matching import compute_skill_gap, load_courses, run_full_analysis
from data_store import (
    load_courses as load_catalog_courses,
    load_skills,
    load_roles,
    load_demand_signals,
)
from course_gap import analyze_course, rank_roles_for_course

app = FastAPI(
    title="SkillBridge API",
    description="Skill-Market Alignment Platform — PS #26134, powered by Gemini AI",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.json"


# ─── Health Check ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "SkillBridge API", "version": "2.0.0"}


# ─── Courses ───────────────────────────────────────────────────

@app.get("/api/courses")
def get_courses(program_type: str = None):
    """Return all skill development programs, optionally filtered by type."""
    courses = load_courses(str(DATA_DIR / "courses.json"))
    if program_type:
        courses = [c for c in courses if c.get("program_type", "").lower() == program_type.lower()]
    return {"courses": courses, "total": len(courses)}


# ─── Gemini Skill Extraction ──────────────────────────────────

@app.post("/api/extract")
async def extract_skills(request: ExtractionRequest):
    """
    Send raw job posting text to Gemini for structured skill extraction.
    This is the core AI feature — the 'wow' endpoint.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Job posting text cannot be empty")

    try:
        result = await extract_skills_from_text(request.text)
        return {"success": True, "data": result.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


# ─── Skill Gap Analysis ───────────────────────────────────────

@app.get("/api/skillgap")
async def get_skill_gap():
    """
    Run full skill gap analysis:
    Uses pre-computed aggregated skills from job postings for fast response.
    """
    aggregated_skills = [
        "CNC programming", "G-code", "M-code",
        "Blueprint reading", "Precision measurement",
        "PLC programming", "SCADA configuration",
        "Industrial wiring", "Motor control circuits",
        "MIG welding", "TIG welding", "Arc welding",
        "Engine diagnostics", "OBD-II scanners",
        "Fuel injection system repair", "Brake system servicing",
        "Pipe fitting", "Drainage system installation",
        "PC assembly", "Network setup", "LAN",
        "Windows installation", "Linux basics",
        "Split AC installation", "Refrigerant handling",
        "PCB troubleshooting", "Soldering",
        "Oscilloscope usage", "Microcontroller basics",
        "Solar panel installation", "DC wiring",
        "Inverter installation", "Net metering",
        "EV battery diagnostics", "Battery Management System",
        "High-voltage safety", "CAN bus communication",
        "IoT sensors", "MQTT protocol",
        "Python scripting", "Data visualization",
        "Drone assembly", "Flight controller programming",
        "3D printing operation", "CAD modeling",
        "5-axis CNC programming", "CAM software",
        "Robotic arm operation", "Robot programming",
        "GD&T", "Six Sigma basics",
        "AutoCAD", "SolidWorks",
        "Water treatment", "RO plant operation",
        "Cybersecurity basics", "Industrial networking",
        "VFD drives", "Star-Delta starter",
        "Hydraulic systems", "Pneumatic systems",
        "Lean manufacturing", "Kaizen methodology",
        "Quality inspection", "SPC basics",
        "Welding inspection", "Defect identification",
        "Customer communication", "Safety protocols",
        "Preventive maintenance", "Predictive maintenance"
    ]

    courses = load_courses(str(DATA_DIR / "courses.json"))
    report = compute_skill_gap(aggregated_skills, courses)

    return report.model_dump()


# ─── Live Skill Gap (single posting) ──────────────────────────

@app.post("/api/skillgap/live")
async def live_skill_gap(request: ExtractionRequest):
    """Extract skills from a single job posting via Gemini, then run gap analysis."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Job posting text cannot be empty")

    try:
        extracted = await extract_skills_from_text(request.text)
        all_skills = extracted.technical_skills + extracted.tools_and_equipment
        courses = load_courses(str(DATA_DIR / "courses.json"))
        report = compute_skill_gap(all_skills, courses)

        return {
            "extracted": extracted.model_dump(),
            "gap_analysis": report.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Employer Feedback ────────────────────────────────────────

@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    """Append employer feedback to the JSON log file."""
    feedback = FeedbackItem(
        recommendation_skill=request.recommendation_skill,
        action=request.action,
        comment=request.comment,
        employer_name=request.employer_name
    )

    existing = []
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing.append(feedback.model_dump())

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return {"success": True, "message": "Feedback recorded", "total_feedback": len(existing)}


@app.get("/api/feedback")
def get_feedback():
    """Return all employer feedback."""
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return {"feedback": data, "total": len(data)}


# ─── Placements ───────────────────────────────────────────────

@app.get("/api/placements")
def get_placements():
    """Return placement data for charts and analysis."""
    placements_file = DATA_DIR / "placements.json"
    if placements_file.exists():
        with open(placements_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"placements": data, "total": len(data)}
    return {"placements": [], "total": 0}


# ─── Dashboard Stats ──────────────────────────────────────────

@app.get("/api/stats")
def get_dashboard_stats():
    """Aggregated stats for the dashboard."""
    courses = load_courses(str(DATA_DIR / "courses.json"))

    total_enrollment = sum(c.get("enrollment", 0) for c in courses)
    avg_placement = sum(c.get("placement_rate", 0) for c in courses) / len(courses) if courses else 0
    total_programs = len(courses)
    program_types = len(set(c.get("program_type", "ITI") for c in courses))

    # Load placements
    placements_file = DATA_DIR / "placements.json"
    total_placed = 0
    if placements_file.exists():
        with open(placements_file, "r", encoding="utf-8") as f:
            placements = json.load(f)
            total_placed = len([p for p in placements if p.get("status") == "active"])

    return {
        "total_programs": total_programs,
        "program_types": program_types,
        "total_enrollment": total_enrollment,
        "avg_placement_rate": round(avg_placement, 1),
        "total_placed": total_placed,
        "job_postings_analyzed": 18,
        "skills_tracked": 60,
        "districts_covered": 8
    }


# ═══════════════════════════════════════════════════════════════
# NEW ENDPOINTS for PS #26134
# ═══════════════════════════════════════════════════════════════




# ─── Market Demand Radar ──────────────────────────────────────

@app.get("/api/demand")
def get_demand(
    sector: str | None = Query(default=None),
    role: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    location: str | None = Query(default=None),
    demand_level: str | None = Query(default=None),
):
    """Return evidence-backed qualitative demand signals with simple filters."""
    signals = load_demand_signals()
    roles = {r.id: r for r in load_roles()}
    skills = {s.id: s for s in load_skills()}

    def match(value: str, query: str | None) -> bool:
        return not query or value.casefold() == query.casefold()

    filtered = []
    for sig in signals:
        r = roles.get(sig.role_id)
        sk = skills.get(sig.skill_id)
        if not r or not sk:
            continue
        if not match(sig.sector, sector):
            continue
        if not (match(r.name, role) or match(sig.role_id, role)):
            continue
        if not (match(sk.canonical_name, skill) or match(sig.skill_id, skill)):
            continue
        if not match(sig.location, location):
            continue
        if not match(sig.demand_level, demand_level):
            continue
        filtered.append({
            **sig.model_dump(mode="json"),
            "role": r.name,
            "skill": sk.canonical_name,
        })

    levels = {"high": 0, "medium": 0, "low": 0}
    for row in filtered:
        levels[row["demand_level"]] += 1

    return {
        "data_status": "demo",
        "geography": "Maharashtra",
        "total": len(filtered),
        "summary": levels,
        "signals": filtered,
    }


# ─── Market Intelligence ──────────────────────────────────────

@app.get("/api/market-intelligence")
def get_market_intelligence():
    """
    Return comprehensive market intelligence data:
    district demand, trending/emerging/declining skills, job trends, placement overview.
    """
    market_file = DATA_DIR / "market_data.json"
    if not market_file.exists():
        raise HTTPException(status_code=404, detail="Market data not found")

    with open(market_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# ─── Skill Comparison Matrix ─────────────────────────────────

@app.get("/api/skill-comparison")
def get_skill_comparison():
    """
    Return side-by-side comparison of industry-required skills vs
    skills taught in each program. Used for the gap matrix heatmap.
    """
    courses = load_courses(str(DATA_DIR / "courses.json"))

    # Aggregated industry skills
    industry_skills = [
        {"skill": "CNC programming", "demand": "high", "sector": "Manufacturing"},
        {"skill": "PLC programming", "demand": "high", "sector": "Automation"},
        {"skill": "EV battery diagnostics", "demand": "high", "sector": "Automobile"},
        {"skill": "Solar panel installation", "demand": "high", "sector": "Renewable Energy"},
        {"skill": "IoT sensors", "demand": "high", "sector": "Automation"},
        {"skill": "5-axis CNC programming", "demand": "high", "sector": "Manufacturing"},
        {"skill": "Robotic arm operation", "demand": "high", "sector": "Manufacturing"},
        {"skill": "MIG welding", "demand": "high", "sector": "Manufacturing"},
        {"skill": "TIG welding", "demand": "high", "sector": "Manufacturing"},
        {"skill": "Industrial wiring", "demand": "high", "sector": "Electrical"},
        {"skill": "VRV/VRF system", "demand": "high", "sector": "HVAC"},
        {"skill": "Python scripting", "demand": "medium", "sector": "IT"},
        {"skill": "CAM software", "demand": "medium", "sector": "Manufacturing"},
        {"skill": "SCADA configuration", "demand": "medium", "sector": "Automation"},
        {"skill": "Blueprint reading", "demand": "medium", "sector": "Manufacturing"},
        {"skill": "Engine diagnostics", "demand": "medium", "sector": "Automobile"},
        {"skill": "PCB troubleshooting", "demand": "medium", "sector": "Electronics"},
        {"skill": "Cybersecurity basics", "demand": "medium", "sector": "IT"},
        {"skill": "Pipe fitting", "demand": "medium", "sector": "Construction"},
        {"skill": "3D printing operation", "demand": "medium", "sector": "Emerging Tech"},
        {"skill": "Drone assembly", "demand": "medium", "sector": "Emerging Tech"},
        {"skill": "CAN bus communication", "demand": "medium", "sector": "Automobile"},
        {"skill": "Data visualization", "demand": "medium", "sector": "IT"},
        {"skill": "Lean manufacturing", "demand": "medium", "sector": "Manufacturing"},
        {"skill": "GD&T", "demand": "medium", "sector": "Manufacturing"},
    ]

    from matching import skill_matches_course, normalize

    comparison = []
    for skill_info in industry_skills:
        skill = skill_info["skill"]
        programs = {}

        for course in courses:
            course_name = course.get("trade_name", "Unknown")
            course_skills = course.get("skills_taught", [])

            if skill_matches_course(skill, course_skills):
                placement = course.get("placement_rate", 0)
                if placement >= 65:
                    programs[course_name] = "taught"
                else:
                    programs[course_name] = "partial"
            else:
                programs[course_name] = "not_taught"

        comparison.append({
            "skill": skill,
            "demand_level": skill_info["demand"],
            "sector": skill_info["sector"],
            "programs": programs,
        })

    # Also compute coverage scores per program
    coverage_scores = {}
    for course in courses:
        course_name = course.get("trade_name", "Unknown")
        course_skills = course.get("skills_taught", [])
        covered_count = 0

        for skill_info in industry_skills:
            if skill_matches_course(skill_info["skill"], course_skills):
                covered_count += 1

        score = round((covered_count / len(industry_skills)) * 100, 1) if industry_skills else 0
        coverage_scores[course_name] = {
            "score": score,
            "covered": covered_count,
            "total": len(industry_skills),
            "program_type": course.get("program_type", "ITI"),
            "is_obsolete": course.get("is_obsolete", False),
            "placement_rate": course.get("placement_rate", 0),
        }

    return {
        "comparison": comparison,
        "coverage_scores": coverage_scores,
        "total_industry_skills": len(industry_skills),
        "total_programs": len(courses),
    }


# ─── Program Recommendations ─────────────────────────────────

@app.get("/api/recommendations")
def get_recommendations(
    rec_type: str = None,
    priority: str = None
):
    """
    Return program improvement recommendations.
    Optionally filter by type and priority.
    """
    rec_file = DATA_DIR / "recommendations.json"
    if not rec_file.exists():
        raise HTTPException(status_code=404, detail="Recommendations data not found")

    with open(rec_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if rec_type:
        data = [r for r in data if r.get("type", "").lower() == rec_type.lower()]
    if priority:
        data = [r for r in data if r.get("priority", "").lower() == priority.lower()]

    # Compute summary counts
    all_recs_file = DATA_DIR / "recommendations.json"
    with open(all_recs_file, "r", encoding="utf-8") as f:
        all_recs = json.load(f)

    type_counts = {}
    priority_counts = {}
    for r in all_recs:
        t = r.get("type", "unknown")
        p = r.get("priority", "medium")
        type_counts[t] = type_counts.get(t, 0) + 1
        priority_counts[p] = priority_counts.get(p, 0) + 1

    return {
        "recommendations": data,
        "total": len(data),
        "type_counts": type_counts,
        "priority_counts": priority_counts,
    }


# ─── District Plans ───────────────────────────────────────────

@app.get("/api/district-plans")
def get_district_plans():
    """Return district-level training plans for Maharashtra."""
    plans_file = DATA_DIR / "district_plans.json"
    if not plans_file.exists():
        raise HTTPException(status_code=404, detail="District plans not found")

    with open(plans_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {"plans": data, "total_districts": len(data)}


# ─── Student Programs ────────────────────────────────────────

@app.get("/api/student/programs")
def get_student_programs(interest: str = None):
    """
    Return skill programs for students, optionally filtered by interest category.
    """
    programs_file = DATA_DIR / "student_programs.json"
    if not programs_file.exists():
        raise HTTPException(status_code=404, detail="Student programs not found")

    with open(programs_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if interest:
        data = [p for p in data if interest in p.get("recommended_for", [])]

    # Sort by demand score (high=3, medium=2, low=1) + future outlook
    demand_order = {"high": 3, "medium": 2, "low": 1}
    outlook_order = {"growing": 3, "stable": 2, "declining": 1}
    data.sort(
        key=lambda p: (
            demand_order.get(p.get("current_demand", "medium"), 2)
            + outlook_order.get(p.get("future_outlook", "stable"), 2)
        ),
        reverse=True,
    )

    return {"programs": data, "total": len(data)}


# ─── Resume Parsing & Matching ────────────────────────────────

@app.post("/api/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Upload a PDF/DOCX resume and get structured parsed data.
    Uses Gemini AI for intelligent extraction.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    try:
        from resume_parser import parse_resume_text, read_resume_file

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Read and parse
        resume_text = read_resume_file(tmp_path)
        parsed = await parse_resume_text(resume_text)

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

        return {"success": True, "data": parsed.model_dump()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")


@app.post("/api/resume/match-programs")
async def match_resume_programs(file: UploadFile = File(...)):
    """
    Upload a resume and get matched against all available skill programs.
    Returns sorted list of programs with match scores.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    try:
        from resume_parser import parse_and_match, read_resume_file

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Load programs
        programs_file = DATA_DIR / "student_programs.json"
        with open(programs_file, "r", encoding="utf-8") as f:
            programs = json.load(f)

        # Parse and match
        result = await parse_and_match(tmp_path, programs)

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

        return {"success": True, **result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume matching failed: {str(e)}")


# ─── Market roles ─────────────────────────────────────────────

@app.get("/api/roles")
def get_market_roles(sector: str | None = Query(default=None)):
    """Return canonical Maharashtra market roles for target-role selection."""
    roles = load_roles()
    if sector:
        roles = [r for r in roles if r.sector.casefold() == sector.casefold()]
    return {"roles": [{"role_id": r.id, "role": r.name, "sector": r.sector} for r in roles], "total": len(roles)}

# ─── Resume–Market Alignment ─────────────────────────────────

@app.post("/api/resume/align")
async def align_resume(
    file: UploadFile = File(...),
    role_id: str | None = Query(default=None),
):
    """Extract a PDF/DOCX resume, then compare it with a market role."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No resume uploaded")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded resume is empty")
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume must be 5 MB or smaller")

    tmp_path = None
    try:
        from resume_parser import read_resume_file, parse_resume_text
        from resume_market import analyze_resume, rank_roles

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = read_resume_file(tmp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract readable text from the resume")

        parsed = await parse_resume_text(text)
        skills = load_skills()
        roles = load_roles()
        signals = load_demand_signals()

        if role_id:
            role = next((r for r in roles if r.id == role_id), None)
            if role is None:
                raise HTTPException(status_code=404, detail="Target role not found")
        else:
            ranked = rank_roles(parsed, roles, skills)
            if not ranked:
                raise HTTPException(status_code=404, detail="No market roles available")
            role = next(r for r in roles if r.id == ranked[0]["role_id"])

        report = analyze_resume(parsed, role, skills, signals)
        report["resume"] = parsed.model_dump()
        report["role_options"] = rank_roles(parsed, roles, skills)
        report["extraction_method"] = "gemini_with_local_fallback"
        return {"success": True, "data": report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume alignment failed: {str(e)}")
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)

# ─── Course–Market Gap Analyzer ──────────────────────────────

@app.get("/api/courses/{course_id}/gap")
def get_course_market_gap(
    course_id: str,
    role_id: str | None = Query(default=None),
):
    """Compare one course curriculum against a market role using deterministic skill coverage."""
    courses = load_catalog_courses()
    course = next((c for c in courses if c.id == course_id), None)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    skills = load_skills()
    roles = load_roles()
    signals = load_demand_signals()
    if role_id:
        role = next((r for r in roles if r.id == role_id), None)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        if course.canonical_sector and role.sector != course.canonical_sector:
            raise HTTPException(status_code=400, detail="Selected role is outside the course sector")
    else:
        ranked = rank_roles_for_course(course, roles, skills, signals)
        if not ranked:
            raise HTTPException(status_code=404, detail="No market roles found for this course")
        role = next(r for r in roles if r.id == ranked[0]["role_id"])

    return analyze_course(course, role, skills, signals)


@app.get("/api/courses/{course_id}/gap")
def get_course_market_gap(
    course_id: str,
    role_id: str | None = Query(default=None),
):
    """Compare one course curriculum against a market role using deterministic skill coverage."""

  
    courses = load_catalog_courses()
    course = next((c for c in courses if c.id == course_id), None)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    skills = load_skills()
    roles = load_roles()
    signals = load_demand_signals()

    ranked = rank_roles_for_course(course, roles, skills, signals)