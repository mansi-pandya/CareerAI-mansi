import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    ForeignKey, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON

from app.database.database import Base


class InterviewTypeEnum(str, enum.Enum):
    hr = "hr"
    technical = "technical"
    coding = "coding"
    behavioral = "behavioral"
    project_based = "project_based"
    mixed = "mixed"


class DifficultyEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class InterviewStatusEnum(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class PriorityEnum(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_career = Column(String(200), nullable=False)
    target_role = Column(String(200), nullable=True)
    interview_type = Column(SAEnum(InterviewTypeEnum), nullable=False, default=InterviewTypeEnum.mixed)
    difficulty = Column(SAEnum(DifficultyEnum), nullable=False, default=DifficultyEnum.intermediate)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    job_description = Column(Text, nullable=True)
    status = Column(SAEnum(InterviewStatusEnum), nullable=False, default=InterviewStatusEnum.in_progress)

    # Scores
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    project_knowledge_score = Column(Float, nullable=True)
    hr_behavioral_score = Column(Float, nullable=True)
    technical_accuracy_score = Column(Float, nullable=True)

    feedback_summary = Column(Text, nullable=True)
    improvement_areas = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.question_number")
    improvements = relationship("InterviewImprovement", back_populates="interview", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # technical/behavioral/project/hr/coding
    topic = Column(String(200), nullable=True)
    difficulty = Column(String(50), nullable=True)
    expected_answer_points = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, unique=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    better_answer_example = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Scores breakdown
    technical_correctness = Column(Float, nullable=True)
    relevance = Column(Float, nullable=True)
    communication_quality = Column(Float, nullable=True)
    completeness = Column(Float, nullable=True)

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")


class InterviewImprovement(Base):
    __tablename__ = "interview_improvements"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    priority = Column(SAEnum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    area = Column(String(200), nullable=False)
    topic = Column(String(200), nullable=True)
    explanation = Column(Text, nullable=True)
    practice_suggestion = Column(Text, nullable=True)
    learning_resource_url = Column(String(500), nullable=True)
    example_better_answer = Column(Text, nullable=True)

    # Relationships
    interview = relationship("Interview", back_populates="improvements")
