import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum as SAEnum, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON

from app.database.database import Base


class SectionType(str, enum.Enum):
    contact = "contact"
    education = "education"
    skills = "skills"
    projects = "projects"
    experience = "experience"
    certifications = "certifications"
    achievements = "achievements"
    summary = "summary"


class Priority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="My Resume")
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan", order_by="ResumeVersion.version_number")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan", order_by="ResumeSection.order_index")
    ats_scores = relationship("ATSScore", back_populates="resume", cascade="all, delete-orphan", order_by="ATSScore.created_at")

    def __repr__(self):
        return f"<Resume id={self.id} title={self.title} user_id={self.user_id}>"


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="versions")
    ats_scores = relationship("ATSScore", back_populates="version", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResumeVersion id={self.id} resume_id={self.resume_id} v={self.version_number}>"


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    section_type = Column(SAEnum(SectionType), nullable=False)
    content = Column(JSON, nullable=False, default=dict)
    order_index = Column(Integer, nullable=False, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="sections")

    def __repr__(self):
        return f"<ResumeSection id={self.id} resume_id={self.resume_id} type={self.section_type}>"


class ATSScore(Base):
    __tablename__ = "ats_scores"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    overall_score = Column(Float, nullable=False, default=0.0)
    structure_score = Column(Float, nullable=False, default=0.0)
    formatting_score = Column(Float, nullable=False, default=0.0)
    keyword_score = Column(Float, nullable=False, default=0.0)
    skills_score = Column(Float, nullable=False, default=0.0)
    projects_score = Column(Float, nullable=False, default=0.0)
    experience_score = Column(Float, nullable=False, default=0.0)
    education_score = Column(Float, nullable=False, default=0.0)
    contact_score = Column(Float, nullable=False, default=0.0)
    job_alignment_score = Column(Float, nullable=False, default=0.0)
    analysis_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="ats_scores")
    version = relationship("ResumeVersion", back_populates="ats_scores")
    recommendations = relationship("ATSRecommendation", back_populates="ats_score", cascade="all, delete-orphan", order_by="ATSRecommendation.priority")

    def __repr__(self):
        return f"<ATSScore id={self.id} resume_id={self.resume_id} score={self.overall_score}>"


class ATSRecommendation(Base):
    __tablename__ = "ats_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    ats_score_id = Column(Integer, ForeignKey("ats_scores.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    current_problem = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=False)
    how_to_fix = Column(Text, nullable=False)
    section_to_modify = Column(String(100), nullable=True)
    priority = Column(SAEnum(Priority), nullable=False, default=Priority.medium)
    estimated_score_impact = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ats_score = relationship("ATSScore", back_populates="recommendations")

    def __repr__(self):
        return f"<ATSRecommendation id={self.id} category={self.category} priority={self.priority}>"
