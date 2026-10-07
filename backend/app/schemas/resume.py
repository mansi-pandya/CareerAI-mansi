from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator


# ─── Nested data schemas ────────────────────────────────────────────────────

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cgpa: Optional[str] = None
    coursework: Optional[List[str]] = None


class ProjectItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    contributions: Optional[str] = None
    results: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None


class CertificationItem(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None


class SkillsData(BaseModel):
    programming: Optional[List[str]] = None
    web_dev: Optional[List[str]] = None
    database: Optional[List[str]] = None
    ai_ml: Optional[List[str]] = None
    data_analytics: Optional[List[str]] = None
    cloud: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    other: Optional[List[str]] = None


# ─── Parsed resume data ──────────────────────────────────────────────────────

class ParsedResumeData(BaseModel):
    contact: Optional[ContactInfo] = None
    education: Optional[List[EducationItem]] = None
    skills: Optional[SkillsData] = None
    projects: Optional[List[ProjectItem]] = None
    experience: Optional[List[ExperienceItem]] = None
    certifications: Optional[List[CertificationItem]] = None
    achievements: Optional[List[str]] = None
    summary: Optional[str] = None


# ─── Resume CRUD schemas ──────────────────────────────────────────────────────

class ResumeCreate(BaseModel):
    title: str = Field(default="My Resume", max_length=200)


class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    is_active: Optional[bool] = None
    parsed_data: Optional[ParsedResumeData] = None


class ResumeVersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeSectionResponse(BaseModel):
    id: int
    resume_id: int
    section_type: str
    content: Dict[str, Any]
    order_index: int

    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetailResponse(ResumeResponse):
    versions: List[ResumeVersionResponse] = []
    sections: List[ResumeSectionResponse] = []

    model_config = {"from_attributes": True}


# ─── Upload ───────────────────────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    resume_id: int
    version_id: int
    title: str
    parsed_data: ParsedResumeData
    raw_text: str
    message: str


# ─── Builder form ─────────────────────────────────────────────────────────────

class ResumeBuilderRequest(BaseModel):
    title: str = Field(default="My Resume", max_length=200)
    contact: Optional[ContactInfo] = None
    education: Optional[List[EducationItem]] = None
    skills: Optional[SkillsData] = None
    projects: Optional[List[ProjectItem]] = None
    experience: Optional[List[ExperienceItem]] = None
    certifications: Optional[List[CertificationItem]] = None
    achievements: Optional[List[str]] = None
    summary: Optional[str] = None


# ─── AI Improve ───────────────────────────────────────────────────────────────

class AIImproveRequest(BaseModel):
    section: str = Field(..., description="Section name (e.g. experience, projects, summary)")
    field: str = Field(..., description="Field name within the section (e.g. responsibilities)")
    current_text: str = Field(..., description="The original text to improve")


class AIImproveResponse(BaseModel):
    section: str
    field: str
    original_text: str
    improved_text: str
    message: str = "Improvement generated successfully"


# ─── ATS Schemas ──────────────────────────────────────────────────────────────

class ATSRecommendationResponse(BaseModel):
    id: int
    ats_score_id: int
    category: str
    current_problem: str
    why_it_matters: str
    how_to_fix: str
    section_to_modify: Optional[str] = None
    priority: str
    estimated_score_impact: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ATSScoreResponse(BaseModel):
    id: int
    resume_id: int
    version_id: Optional[int] = None
    overall_score: float
    structure_score: float
    formatting_score: float
    keyword_score: float
    skills_score: float
    projects_score: float
    experience_score: float
    education_score: float
    contact_score: float
    job_alignment_score: float
    analysis_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    recommendations: List[ATSRecommendationResponse] = []

    model_config = {"from_attributes": True}


class ATSAnalysisRequest(BaseModel):
    job_description: Optional[str] = Field(default=None, description="Optional job description for job-specific scoring")


class ATSScoreHistoryItem(BaseModel):
    id: int
    version_number: Optional[int] = None
    overall_score: float
    structure_score: float
    formatting_score: float
    keyword_score: float
    skills_score: float
    projects_score: float
    experience_score: float
    education_score: float
    contact_score: float
    job_alignment_score: float
    created_at: datetime

    model_config = {"from_attributes": True}
