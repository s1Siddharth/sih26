from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExtractedSkills(BaseModel):
    """Structured skills extracted from a job posting by Gemini."""
    job_title: str = Field(description="The job title from the posting")
    industry: str = Field(description="Industry sector (e.g., Manufacturing, IT, Automobile)")
    experience_level: str = Field(description="Experience level (e.g., Fresher, 1-3 years, 3-5 years)")
    technical_skills: list[str] = Field(description="List of technical/hard skills required")
    soft_skills: list[str] = Field(description="List of soft skills mentioned")
    certifications: list[str] = Field(default_factory=list, description="Certifications mentioned")
    tools_and_equipment: list[str] = Field(default_factory=list, description="Specific tools or equipment mentioned")
    qualification: str = Field(default="", description="Educational qualification required")
    salary_range: str = Field(default="", description="Salary range if mentioned")


class ExtractionRequest(BaseModel):
    """Request body for the /api/extract endpoint."""
    text: str = Field(description="Raw job posting text to extract skills from")


class SkillGapResult(BaseModel):
    """Result of comparing a job skill against course offerings."""
    skill: str
    status: str = Field(description="One of: covered, partial, gap, emerging")
    status_emoji: str = Field(description="One of: ✅, ⚠️, ❌, 🆕")
    matching_courses: list[str] = Field(default_factory=list)
    market_demand: str = Field(default="medium", description="high, medium, or low")
    notes: str = Field(default="")


class SkillGapReport(BaseModel):
    """Full skill gap analysis report."""
    total_skills_analyzed: int
    covered: int
    partial: int
    gaps: int
    emerging: int
    results: list[SkillGapResult]
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class FeedbackItem(BaseModel):
    """Employer feedback on a skill gap recommendation."""
    recommendation_skill: str
    action: str = Field(description="approve or reject")
    comment: str = Field(default="")
    employer_name: str = Field(default="Anonymous")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class FeedbackRequest(BaseModel):
    """Request body for the /api/feedback endpoint."""
    recommendation_skill: str
    action: str
    comment: str = ""
    employer_name: str = "Anonymous"


# ─── New Models for PS #26134 ────────────────────────────────

class DistrictDemand(BaseModel):
    """District-wise industry demand data."""
    district: str
    total_openings: int
    sectors: dict[str, int]
    growth_trend: str
    top_roles: list[str]


class TrendingSkill(BaseModel):
    """A trending skill with growth data."""
    skill: str
    growth_percent: int
    sector: str
    demand: str


class EmergingSkill(BaseModel):
    """An emerging / Industry 4.0 skill."""
    skill: str
    sector: str
    readiness: str
    impact: str


class DecliningSkill(BaseModel):
    """A skill losing market relevance."""
    skill: str
    decline_percent: int
    sector: str
    reason: str


class MarketIntelligenceReport(BaseModel):
    """Complete market intelligence data."""
    district_demand: list[DistrictDemand]
    trending_skills: list[TrendingSkill]
    emerging_skills: list[EmergingSkill]
    declining_skills: list[DecliningSkill]
    job_trends: list[dict]
    placement_overview: list[dict]


class ProgramRecommendation(BaseModel):
    """A program improvement recommendation."""
    id: str
    type: str = Field(description="update_curriculum, new_course, add_equipment, train_instructor, flag_obsolete, reduce_capacity")
    priority: str = Field(description="critical, high, medium")
    target_skill: str
    current_gap: str
    recommendation: str
    reason: str
    estimated_impact: str
    affected_programs: list[str]
    district_relevance: list[str]
    employer_validated: bool


class SkillComparisonEntry(BaseModel):
    """A single skill's comparison across programs."""
    skill: str
    demand_level: str
    sector: str
    programs: dict[str, str] = Field(description="program_name -> coverage status (taught/partial/not_taught)")


class ParsedResume(BaseModel):
    """Structured data extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    total_experience_years: Optional[float] = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    experiences: list[dict] = Field(default_factory=list)


class ProgramMatch(BaseModel):
    """Result of matching a resume against a skill program."""
    program_name: str
    program_type: str
    match_score: float = Field(description="0-100 match percentage")
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    verdict: str = Field(default="")
    current_demand: str = Field(default="medium")
    future_outlook: str = Field(default="stable")
    avg_salary_range: str = Field(default="")
