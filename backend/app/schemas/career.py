from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Career ──────────────────────────────────────────────────────────────────

class CareerBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    industry: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: Dict[str, Any] = {}
    market_demand_score: float = 0.0
    avg_salary_min: int = 0
    avg_salary_max: int = 0
    growth_rate: float = 0.0


class CareerResponse(CareerBase):
    model_config = {"from_attributes": True}
    id: int


class CareerListItem(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    slug: str
    industry: Optional[str] = None
    market_demand_score: float
    avg_salary_min: int
    avg_salary_max: int
    growth_rate: float
    required_skills: List[str] = []


# ── CareerMatch ──────────────────────────────────────────────────────────────

class CareerMatchResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    career_id: int
    match_score: float
    skill_score: float
    education_score: float
    project_score: float
    experience_score: float
    interest_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    reasoning: Optional[str] = None
    created_at: datetime

    # Joined career info
    career_name: Optional[str] = None
    career_slug: Optional[str] = None
    career_industry: Optional[str] = None
    career_description: Optional[str] = None
    avg_salary_min: Optional[int] = None
    avg_salary_max: Optional[int] = None
    market_demand_score: Optional[float] = None
    growth_rate: Optional[float] = None


# ── SkillGap ─────────────────────────────────────────────────────────────────

class SkillGapItem(BaseModel):
    skill_name: str
    importance: str          # critical / important / nice-to-have
    current_level: int       # 0–5
    required_level: int      # 1–5
    gap: int
    priority: str            # high / medium / low


class SkillGapResponse(BaseModel):
    career_name: str
    career_slug: str
    total_required: int
    matched_count: int
    missing_count: int
    match_percentage: float
    matched_skills: List[Dict[str, Any]] = []
    missing_skills: List[SkillGapItem] = []


# ── LearningResource ─────────────────────────────────────────────────────────

class LearningResourceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    skill_name: str
    resource_name: str
    provider: str
    url: str
    topics: List[str] = []
    difficulty: str
    is_free: bool
    duration_hours: float
    description: Optional[str] = None
    why_recommended: Optional[str] = None


# ── LearningRoadmap ──────────────────────────────────────────────────────────

class RoadmapPhase(BaseModel):
    phase_number: int
    phase_name: str
    description: str
    skills: List[str]
    estimated_weeks: int
    topics: Dict[str, List[str]] = {}
    resources: List[Dict[str, Any]] = []


class LearningRoadmapResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    career_id: int
    career_name: Optional[str] = None
    career_slug: Optional[str] = None
    title: str
    phases: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime


# ── LearningProgress ─────────────────────────────────────────────────────────

class LearningProgressCreate(BaseModel):
    skill_name: str
    proficiency_level: int   # 0–100
    notes: Optional[str] = None


class LearningProgressResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    skill_name: str
    proficiency_level: int
    notes: Optional[str] = None
    last_updated: datetime


# ── What-If ───────────────────────────────────────────────────────────────────

class WhatIfResponse(BaseModel):
    career_name: str
    career_slug: str
    current_match: float
    estimated_match: float
    skills_added: List[str]
    improvement: float
    explanation: str
    disclaimer: str = (
        "This is an estimated projection based on skill weights. "
        "Actual career outcomes depend on many factors beyond this score."
    )
