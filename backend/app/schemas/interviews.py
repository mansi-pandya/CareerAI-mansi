from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

from app.models.interviews import InterviewTypeEnum, DifficultyEnum, InterviewStatusEnum, PriorityEnum


# ── Request schemas ────────────────────────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    target_career: str
    target_role: Optional[str] = None
    interview_type: InterviewTypeEnum = InterviewTypeEnum.mixed
    difficulty: DifficultyEnum = DifficultyEnum.intermediate
    job_id: Optional[int] = None
    job_description: Optional[str] = None


class AnswerSubmitRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)


# ── Response schemas ───────────────────────────────────────────────────────────

class QuestionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    interview_id: int
    question_number: int
    question_text: str
    question_type: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    total_questions: Optional[int] = None
    is_answered: Optional[bool] = None


class AnswerFeedbackResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    question_id: int
    interview_id: int
    score: float
    feedback: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    better_answer_example: Optional[str] = None
    technical_correctness: Optional[float] = None
    relevance: Optional[float] = None
    communication_quality: Optional[float] = None
    completeness: Optional[float] = None
    next_question: Optional[QuestionResponse] = None


class ImprovementResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    interview_id: int
    priority: PriorityEnum
    area: str
    topic: Optional[str] = None
    explanation: Optional[str] = None
    practice_suggestion: Optional[str] = None
    learning_resource_url: Optional[str] = None
    example_better_answer: Optional[str] = None


class QuestionWithAnswerResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    question_number: int
    question_text: str
    question_type: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    answer: Optional[AnswerFeedbackResponse] = None


class InterviewCompleteResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    target_career: str
    target_role: Optional[str] = None
    interview_type: InterviewTypeEnum
    difficulty: DifficultyEnum
    status: InterviewStatusEnum
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    relevance_score: Optional[float] = None
    problem_solving_score: Optional[float] = None
    project_knowledge_score: Optional[float] = None
    hr_behavioral_score: Optional[float] = None
    technical_accuracy_score: Optional[float] = None
    feedback_summary: Optional[str] = None
    improvement_areas: Optional[Any] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[QuestionWithAnswerResponse] = []
    improvements: List[ImprovementResponse] = []


class InterviewSessionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    target_career: str
    target_role: Optional[str] = None
    interview_type: InterviewTypeEnum
    difficulty: DifficultyEnum
    status: InterviewStatusEnum
    created_at: datetime
    total_questions: int
    answered_questions: int
    first_question: Optional[QuestionResponse] = None


class InterviewHistoryItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    target_career: str
    target_role: Optional[str] = None
    interview_type: InterviewTypeEnum
    difficulty: DifficultyEnum
    status: InterviewStatusEnum
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_questions: int
    answered_questions: int
