from __future__ import annotations

from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.jobs import JobTypeEnum, WorkModeEnum, SavedJobStatusEnum


# ── JobSource ────────────────────────────────────────────────────────────────

class JobSourceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    slug: str
    is_active: bool
    description: Optional[str] = None


# ── Job ──────────────────────────────────────────────────────────────────────

class JobResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    external_id: Optional[str] = None
    source_id: int
    title: str
    company: str
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    job_type: Optional[JobTypeEnum] = None
    work_mode: Optional[WorkModeEnum] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    experience_min_years: Optional[float] = None
    experience_max_years: Optional[float] = None
    required_skills: List[str] = []
    description: Optional[str] = None
    application_url: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime

    # Source info (joined)
    source_name: Optional[str] = None
    source_slug: Optional[str] = None
    is_demo: bool = False


class JobListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    company: str
    location: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    job_type: Optional[JobTypeEnum] = None
    work_mode: Optional[WorkModeEnum] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    required_skills: List[str] = []
    posted_date: Optional[datetime] = None
    source_name: Optional[str] = None
    source_slug: Optional[str] = None
    is_demo: bool = False
    # Match info (optional, populated when user is authenticated)
    overall_score: Optional[float] = None
    match_reasons: Optional[List[str]] = None


# ── JobFilter ────────────────────────────────────────────────────────────────

class JobFilter(BaseModel):
    keywords: Optional[str] = None
    job_type: Optional[List[JobTypeEnum]] = None
    work_mode: Optional[List[WorkModeEnum]] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    company: Optional[str] = None
    source: Optional[str] = None   # "adzuna" | "demo" | None (all)
    page: int = 1
    limit: int = 20
    sort_by: str = "match"  # "match" | "newest" | "salary"

    @field_validator("limit")
    @classmethod
    def cap_limit(cls, v: int) -> int:
        return min(v, 100)


# ── JobMatch ─────────────────────────────────────────────────────────────────

class JobMatchResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    job_id: int
    overall_score: float
    skill_score: float
    role_score: float
    education_score: float
    experience_score: float
    location_score: float
    preference_score: float
    match_reasons: List[str] = []
    created_at: datetime


# ── SavedJob ─────────────────────────────────────────────────────────────────

class SavedJobCreate(BaseModel):
    notes: Optional[str] = None


class SavedJobStatusUpdate(BaseModel):
    status: SavedJobStatusEnum
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    job_id: int
    status: SavedJobStatusEnum
    notes: Optional[str] = None
    saved_at: datetime
    applied_at: Optional[datetime] = None

    # Denormalized job info
    job: Optional[JobListItem] = None


# ── Market Analysis ───────────────────────────────────────────────────────────

class SkillDemandItem(BaseModel):
    skill: str
    count: int
    demand_percentage: float
    have_skill: bool = False


class MarketSkillsResponse(BaseModel):
    total_jobs_analyzed: int
    top_skills: List[SkillDemandItem]
    my_skills_in_demand: List[str]
    missing_high_demand_skills: List[str]


class TrendItem(BaseModel):
    label: str
    count: int
    percentage: float


class MarketTrendsResponse(BaseModel):
    total_jobs: int
    job_type_trends: List[TrendItem]
    work_mode_trends: List[TrendItem]
    top_companies: List[Dict[str, Any]]


# ── Job Search Result ─────────────────────────────────────────────────────────

class JobSearchResult(BaseModel):
    jobs: List[JobListItem]
    total: int
    page: int
    limit: int
    has_next: bool
    has_demo: bool = False
