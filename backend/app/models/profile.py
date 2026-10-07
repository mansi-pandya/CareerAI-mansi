from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Table
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    college = Column(String(300), nullable=True)
    degree = Column(String(200), nullable=True)
    major = Column(String(200), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    resume_path = Column(String(500), nullable=True)
    avatar_path = Column(String(500), nullable=True)
    preferred_career = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    is_profile_complete = Column(Boolean, default=False)

    # Career readiness scores (0-100)
    ats_score = Column(Float, default=0.0)
    skill_match_score = Column(Float, default=0.0)
    career_match_score = Column(Float, default=0.0)
    job_match_score = Column(Float, default=0.0)
    interview_readiness_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("StudentSkill", back_populates="profile", cascade="all, delete-orphan")
    career_preferences = relationship("CareerPreference", back_populates="profile", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    institution = Column(String(300), nullable=False)
    degree = Column(String(200), nullable=False)
    field_of_study = Column(String(200), nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)
    is_current = Column(Boolean, default=False)

    profile = relationship("StudentProfile", back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=True)  # e.g. "Programming", "Soft Skills"
    description = Column(Text, nullable=True)

    student_skills = relationship("StudentSkill", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(String(50), default="beginner")  # beginner, intermediate, advanced, expert
    years_experience = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)

    profile = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")


class CareerPreference(Base):
    __tablename__ = "career_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    career_title = Column(String(200), nullable=False)
    industry = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False)
    priority_rank = Column(Integer, default=1)

    profile = relationship("StudentProfile", back_populates="career_preferences")
