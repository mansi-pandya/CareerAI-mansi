from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.opportunities import (
    InputTypeEnum,
    VerificationStatusEnum,
    ApplyRecommendationEnum,
)


class ExtractedOpportunityData(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)
    education_required: Optional[str] = None
    experience_required: Optional[str] = None
    deadline: Optional[str] = None
    application_url: Optional[str] = None
    contact_email: Optional[str] = None
    source_text: Optional[str] = None  # truncated raw text used for extraction


class VerificationResult(BaseModel):
    status: VerificationStatusEnum
    score: float
    checks_performed: Dict[str, Any] = Field(default_factory=dict)
    warning_signs: List[str] = Field(default_factory=list)
    positive_signals: List[str] = Field(default_factory=list)
    explanation: str
    disclaimer: str = (
        "This is an automated check based on available signals only. "
        "Always verify the opportunity independently before sharing personal information."
    )


class ApplyRecommendation(BaseModel):
    recommendation: ApplyRecommendationEnum
    reasoning: str
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    upskill_suggestions: List[Dict[str, str]] = Field(default_factory=list)


class OpportunityDocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime


class OpportunityCheckResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    input_type: InputTypeEnum
    raw_input: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    verification_status: Optional[VerificationStatusEnum] = None
    verification_score: Optional[float] = None
    verification_details: Optional[Dict[str, Any]] = None
    apply_recommendation: Optional[ApplyRecommendationEnum] = None
    apply_reasoning: Optional[str] = None
    created_at: datetime
    documents: List[OpportunityDocumentResponse] = Field(default_factory=list)


class OpportunityCheckListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    input_type: InputTypeEnum
    extracted_data: Optional[Dict[str, Any]] = None
    verification_status: Optional[VerificationStatusEnum] = None
    verification_score: Optional[float] = None
    apply_recommendation: Optional[ApplyRecommendationEnum] = None
    created_at: datetime
