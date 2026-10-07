from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    industry = Column(String(200), nullable=True)
    required_skills = Column(JSON, default=list)       # list of skill names
    preferred_skills = Column(JSON, default=list)
    education_requirements = Column(JSON, default=dict) # {degrees: [], fields: []}
    market_demand_score = Column(Float, default=0.0)   # 0–10
    avg_salary_min = Column(Integer, default=0)
    avg_salary_max = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)           # % per year

    matches = relationship("CareerMatch", back_populates="career", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="career", cascade="all, delete-orphan")
    roadmaps = relationship("LearningRoadmap", back_populates="career", cascade="all, delete-orphan")


class CareerMatch(Base):
    __tablename__ = "career_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    match_score = Column(Float, default=0.0)           # composite 0–100
    skill_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    project_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    interest_score = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career", back_populates="matches")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    skill_name = Column(String(200), nullable=False)
    importance = Column(String(50), default="important")   # critical / important / nice-to-have
    current_level = Column(Integer, default=0)             # 0–5
    required_level = Column(Integer, default=3)            # 1–5
    gap = Column(Integer, default=0)
    priority = Column(String(50), default="medium")        # high / medium / low
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career", back_populates="skill_gaps")


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(200), nullable=False, index=True)
    resource_name = Column(String(500), nullable=False)
    provider = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=False)
    topics = Column(JSON, default=list)
    difficulty = Column(String(50), default="beginner")    # beginner / intermediate / advanced
    is_free = Column(Boolean, default=True)
    duration_hours = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    why_recommended = Column(Text, nullable=True)


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    title = Column(String(500), nullable=False)
    phases = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career", back_populates="roadmaps")


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(200), nullable=False)
    proficiency_level = Column(Integer, default=0)    # 0–100
    notes = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
