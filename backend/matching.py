"""
Rule-based skill gap matching engine.
Compares extracted job skills against ITI course offerings.
"""

import json
from pathlib import Path
from models import SkillGapResult, SkillGapReport


# Skills that are clearly emerging / Industry 4.0 / not in traditional ITI curriculum
EMERGING_KEYWORDS = [
    "iot", "industry 4.0", "ev", "electric vehicle", "battery management",
    "bms", "drone", "uav", "3d printing", "additive manufacturing",
    "robotic", "robot programming", "can bus", "mqtt", "opc-ua",
    "python", "node.js", "data visualization", "machine learning",
    "ai", "artificial intelligence", "cloud", "cybersecurity",
    "digital twin", "augmented reality", "blockchain",
    "lidar", "autonomous", "deep learning", "firmware",
    "flight controller", "ardupilot", "px4", "gis",
    "bim", "building information", "smart manufacturing",
    "predictive maintenance", "edge computing"
]

# High-demand skills based on current Indian job market trends
HIGH_DEMAND_SKILLS = [
    "cnc programming", "plc programming", "solar", "ev",
    "electric vehicle", "automation", "iot", "industry 4.0",
    "hvac", "vrf", "data", "cyber", "networking",
    "welding", "mig", "tig", "robotics", "5-axis",
    "cam software", "scada", "hmi", "inverter",
    "battery", "renewable", "energy efficiency"
]


def load_courses(filepath: str = None) -> list[dict]:
    """Load course data from JSON file."""
    if filepath is None:
        filepath = Path(__file__).parent / "data" / "courses.json"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    """Normalize text for matching: lowercase, strip extra whitespace."""
    return text.lower().strip()


def skill_matches_course(skill: str, course_skills: list[str]) -> bool:
    """
    Check if an extracted skill matches any skill in a course.
    Uses substring/fuzzy matching for better coverage.
    """
    skill_lower = normalize(skill)
    
    for course_skill in course_skills:
        cs_lower = normalize(course_skill)
        
        # Exact match
        if skill_lower == cs_lower:
            return True
        
        # Substring match (either direction)
        if skill_lower in cs_lower or cs_lower in skill_lower:
            return True
        
        # Word overlap: if >50% of words match
        skill_words = set(skill_lower.split())
        course_words = set(cs_lower.split())
        if skill_words and course_words:
            overlap = skill_words & course_words
            # At least one meaningful word overlaps (ignore tiny words)
            meaningful_overlap = {w for w in overlap if len(w) > 2}
            if meaningful_overlap:
                return True
    
    return False


def is_emerging_skill(skill: str) -> bool:
    """Check if a skill falls into emerging/Industry 4.0 category."""
    skill_lower = normalize(skill)
    return any(kw in skill_lower for kw in EMERGING_KEYWORDS)


def get_market_demand(skill: str) -> str:
    """Estimate market demand level for a skill."""
    skill_lower = normalize(skill)
    if any(kw in skill_lower for kw in HIGH_DEMAND_SKILLS):
        return "high"
    return "medium"


def compute_skill_gap(
    extracted_skills: list[str],
    courses: list[dict] = None
) -> SkillGapReport:
    """
    Compare extracted job skills against course offerings.
    
    For each skill, determine:
    - ✅ Covered: Skill is taught in at least one course with good placement rate (>65%)
    - ⚠️ Partial: Skill is taught but course has low enrollment or placement rate (<65%)
    - ❌ Gap: Skill is NOT taught in any course
    - 🆕 Emerging: Skill is new/Industry 4.0, not in traditional ITI curriculum
    
    Returns a SkillGapReport with categorized results.
    """
    if courses is None:
        courses = load_courses()
    
    results = []
    counts = {"covered": 0, "partial": 0, "gap": 0, "emerging": 0}
    
    for skill in extracted_skills:
        matching_courses = []
        best_status = None
        
        # Check if emerging first
        if is_emerging_skill(skill):
            # Still check if any course teaches it
            for course in courses:
                if skill_matches_course(skill, course.get("skills_taught", [])):
                    matching_courses.append(course["trade_name"])
            
            if matching_courses:
                # Emerging but partially covered
                best_status = "partial"
                emoji = "⚠️"
                notes = "Emerging skill with some course coverage"
            else:
                best_status = "emerging"
                emoji = "🆕"
                notes = "Emerging/Industry 4.0 skill - not in current ITI curriculum"
            
        else:
            # Check against all courses
            for course in courses:
                if skill_matches_course(skill, course.get("skills_taught", [])):
                    matching_courses.append(course["trade_name"])
                    placement = course.get("placement_rate", 0)
                    enrollment = course.get("enrollment", 0)
                    
                    if placement >= 65 and enrollment >= 1000:
                        best_status = "covered"
                    elif best_status != "covered":
                        best_status = "partial"
            
            if best_status == "covered":
                emoji = "✅"
                notes = "Well covered by ITI courses"
            elif best_status == "partial":
                emoji = "⚠️"
                notes = "Taught but course has low enrollment or placement rate"
            else:
                best_status = "gap"
                emoji = "❌"
                notes = "Not currently taught in any ITI course"
        
        demand = get_market_demand(skill)
        counts[best_status] += 1
        
        results.append(SkillGapResult(
            skill=skill,
            status=best_status,
            status_emoji=emoji,
            matching_courses=matching_courses,
            market_demand=demand,
            notes=notes
        ))
    
    # Sort: gaps and emerging first (most actionable), then partial, then covered
    status_order = {"gap": 0, "emerging": 1, "partial": 2, "covered": 3}
    results.sort(key=lambda r: status_order.get(r.status, 99))
    
    return SkillGapReport(
        total_skills_analyzed=len(extracted_skills),
        covered=counts["covered"],
        partial=counts["partial"],
        gaps=counts["gap"],
        emerging=counts["emerging"],
        results=results
    )


def run_full_analysis(job_postings_skills: list[list[str]], courses: list[dict] = None) -> SkillGapReport:
    """
    Run gap analysis across multiple job postings.
    Aggregates all unique skills, then matches against courses.
    """
    if courses is None:
        courses = load_courses()
    
    # Collect all unique skills across all job postings
    all_skills = set()
    for skills_list in job_postings_skills:
        for skill in skills_list:
            all_skills.add(skill)
    
    return compute_skill_gap(list(all_skills), courses)
