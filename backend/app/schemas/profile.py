from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[float] = None
    is_current: bool = False


class EducationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[float] = None
    is_current: bool


class SkillResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    category: Optional[str] = None


class StudentSkillCreate(BaseModel):
    skill_name: str
    proficiency: str = "beginner"
    years_experience: float = 0.0


class StudentSkillResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    skill: SkillResponse
    proficiency: str
    years_experience: float
    is_verified: bool


class CareerPreferenceCreate(BaseModel):
    career_title: str
    industry: Optional[str] = None
    is_primary: bool = False
    priority_rank: int = 1


class CareerPreferenceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    career_title: str
    industry: Optional[str] = None
    is_primary: bool
    priority_rank: int


class ProfileCreate(BaseModel):
    college: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_career: Optional[str] = None
    location: Optional[str] = None


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    college: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_career: Optional[str] = None
    location: Optional[str] = None
    is_profile_complete: bool
    ats_score: float
    skill_match_score: float
    career_match_score: float
    job_match_score: float
    interview_readiness_score: float
    overall_score: float
    education: List[EducationResponse] = []
    skills: List[StudentSkillResponse] = []
    career_preferences: List[CareerPreferenceResponse] = []
    created_at: datetime
    updated_at: datetime
