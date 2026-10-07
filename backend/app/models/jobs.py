import enum
import hashlib
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, Text,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import JSON as GenericJSON

from app.database.database import Base


class JobTypeEnum(str, enum.Enum):
    internship = "internship"
    full_time = "full_time"
    part_time = "part_time"
    freelance = "freelance"
    contract = "contract"
    apprenticeship = "apprenticeship"


class WorkModeEnum(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    on_site = "on_site"


class SavedJobStatusEnum(str, enum.Enum):
    saved = "saved"
    applied = "applied"
    interested = "interested"
    ignored = "ignored"


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    api_key_env_var = Column(String(200), nullable=True)
    base_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    jobs = relationship("Job", back_populates="source")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(300), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    title = Column(String(300), nullable=False, index=True)
    company = Column(String(300), nullable=False, index=True)
    location = Column(String(300), nullable=True)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    country = Column(String(100), nullable=True)
    job_type = Column(SAEnum(JobTypeEnum), nullable=True)
    work_mode = Column(SAEnum(WorkModeEnum), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD")
    experience_min_years = Column(Float, nullable=True)
    experience_max_years = Column(Float, nullable=True)
    required_skills = Column(GenericJSON, default=list)
    description = Column(Text, nullable=True)
    application_url = Column(String(1000), nullable=True)
    source_url = Column(String(1000), nullable=True)
    posted_date = Column(DateTime, nullable=True)
    expires_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    dedup_hash = Column(String(64), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("JobSource", back_populates="jobs")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")

    @staticmethod
    def compute_hash(company: str, title: str, location: str) -> str:
        raw = f"{company.lower().strip()}|{title.lower().strip()}|{(location or '').lower().strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    skill_score = Column(Float, default=0.0)
    role_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    preference_score = Column(Float, default=0.0)
    match_reasons = Column(GenericJSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="matches")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(SAEnum(SavedJobStatusEnum), default=SavedJobStatusEnum.saved)
    notes = Column(Text, nullable=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime, nullable=True)

    job = relationship("Job", back_populates="saved_by")


class JobSearchLog(Base):
    __tablename__ = "job_search_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_params = Column(GenericJSON, default=dict)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
