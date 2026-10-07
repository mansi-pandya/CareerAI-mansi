"""
Interviews API router — all /api/interviews endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.profile import StudentProfile, StudentSkill, Skill
from app.models.resume import Resume, ResumeSection
from app.models.interviews import (
    Interview, InterviewQuestion, InterviewAnswer, InterviewImprovement,
    InterviewStatusEnum, PriorityEnum,
)
from app.schemas.interviews import (
    InterviewStartRequest,
    AnswerSubmitRequest,
    InterviewSessionResponse,
    QuestionResponse,
    AnswerFeedbackResponse,
    InterviewCompleteResponse,
    InterviewHistoryItem,
    ImprovementResponse,
    QuestionWithAnswerResponse,
)
from app.interviews.question_generator import generate_questions
from app.interviews.evaluator import evaluate_answer
from app.interviews.feedback_generator import generate_feedback

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_student_profile_data(user: User, db: Session) -> dict:
    """Return skills and projects from the student's profile and resumes."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        return {"skills": [], "projects": [], "profile": None}

    # Skills
    student_skills_raw = (
        db.query(StudentSkill)
        .filter(StudentSkill.profile_id == profile.id)
        .join(Skill)
        .all()
    )
    skills = [
        {"name": ss.skill.name, "proficiency": ss.proficiency}
        for ss in student_skills_raw
    ]

    # Projects from resume sections
    projects: List[dict] = []
    resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    for resume in resumes:
        sections = (
            db.query(ResumeSection)
            .filter(
                ResumeSection.resume_id == resume.id,
                ResumeSection.section_type == "projects",
            )
            .all()
        )
        for section in sections:
            content = section.content or {}
            items = content.get("items", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("name"):
                        projects.append({
                            "name": item.get("name", ""),
                            "description": item.get("description", ""),
                            "technologies": item.get("technologies", []),
                        })

    return {"skills": skills, "projects": projects, "profile": profile}


def _get_interview_or_404(interview_id: int, user: User, db: Session) -> Interview:
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


def _next_unanswered_question(interview: Interview) -> Optional[InterviewQuestion]:
    for q in interview.questions:
        if q.answer is None:
            return q
    return None


def _question_to_response(q: InterviewQuestion, total: int) -> dict:
    return {
        "id": q.id,
        "interview_id": q.interview_id,
        "question_number": q.question_number,
        "question_text": q.question_text,
        "question_type": q.question_type,
        "topic": q.topic,
        "difficulty": q.difficulty,
        "total_questions": total,
        "is_answered": q.answer is not None,
    }


def _answer_to_response(answer: InterviewAnswer, next_q: Optional[InterviewQuestion], total: int) -> dict:
    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "interview_id": answer.interview_id,
        "score": answer.score or 0,
        "feedback": answer.feedback or "",
        "strengths": answer.strengths or [],
        "weaknesses": answer.weaknesses or [],
        "better_answer_example": answer.better_answer_example,
        "technical_correctness": answer.technical_correctness,
        "relevance": answer.relevance,
        "communication_quality": answer.communication_quality,
        "completeness": answer.completeness,
        "next_question": _question_to_response(next_q, total) if next_q else None,
    }


def _interview_history_item(interview: Interview) -> dict:
    total = len(interview.questions)
    answered = sum(1 for q in interview.questions if q.answer is not None)
    return {
        "id": interview.id,
        "target_career": interview.target_career,
        "target_role": interview.target_role,
        "interview_type": interview.interview_type,
        "difficulty": interview.difficulty,
        "status": interview.status,
        "overall_score": interview.overall_score,
        "technical_score": interview.technical_score,
        "communication_score": interview.communication_score,
        "created_at": interview.created_at,
        "completed_at": interview.completed_at,
        "total_questions": total,
        "answered_questions": answered,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new interview session — creates interview + generates questions."""
    student_data = _get_student_profile_data(current_user, db)

    if not student_data["profile"]:
        raise HTTPException(
            status_code=400,
            detail="Please complete your profile before starting an interview.",
        )

    if not student_data["skills"]:
        raise HTTPException(
            status_code=400,
            detail="Please add at least one skill to your profile before starting an interview.",
        )

    # Generate questions
    questions_data = await generate_questions(
        career=payload.target_career,
        role=payload.target_role,
        interview_type=payload.interview_type.value,
        difficulty=payload.difficulty.value,
        skills=student_data["skills"],
        projects=student_data["projects"],
        job_description=payload.job_description,
    )

    if not questions_data:
        raise HTTPException(status_code=500, detail="Failed to generate interview questions.")

    # Create Interview record
    interview = Interview(
        user_id=current_user.id,
        target_career=payload.target_career,
        target_role=payload.target_role,
        interview_type=payload.interview_type,
        difficulty=payload.difficulty,
        job_id=payload.job_id,
        job_description=payload.job_description,
        status=InterviewStatusEnum.in_progress,
    )
    db.add(interview)
    db.flush()

    # Create question records
    for i, q_data in enumerate(questions_data, start=1):
        question = InterviewQuestion(
            interview_id=interview.id,
            question_number=i,
            question_text=q_data.get("text", ""),
            question_type=q_data.get("type", "technical"),
            topic=q_data.get("topic"),
            difficulty=q_data.get("difficulty"),
            expected_answer_points=q_data.get("expected_answer_points", []),
        )
        db.add(question)

    db.commit()
    db.refresh(interview)

    total = len(interview.questions)
    first_q = interview.questions[0] if interview.questions else None

    return {
        "id": interview.id,
        "user_id": interview.user_id,
        "target_career": interview.target_career,
        "target_role": interview.target_role,
        "interview_type": interview.interview_type,
        "difficulty": interview.difficulty,
        "status": interview.status,
        "created_at": interview.created_at,
        "total_questions": total,
        "answered_questions": 0,
        "first_question": _question_to_response(first_q, total) if first_q else None,
    }


@router.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of user's interview history."""
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .options(joinedload(Interview.questions).joinedload(InterviewQuestion.answer))
        .order_by(Interview.created_at.desc())
        .all()
    )
    return [_interview_history_item(iv) for iv in interviews]


@router.get("/careers")
def list_interview_careers(db: Session = Depends(get_db)):
    """List available career options for interview target selection."""
    from app.career.recommender import CAREER_PROFILES
    return [
        {"slug": slug, "name": data["name"], "industry": data.get("industry", "")}
        for slug, data in CAREER_PROFILES.items()
    ]


@router.get("/{interview_id}/next-question")
def get_next_question(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the next unanswered question for an interview."""
    interview = _get_interview_or_404(interview_id, current_user, db)

    if interview.status != InterviewStatusEnum.in_progress:
        raise HTTPException(status_code=400, detail="Interview is not in progress.")

    next_q = _next_unanswered_question(interview)
    if not next_q:
        return {"done": True, "message": "All questions answered. Call /complete to finish."}

    total = len(interview.questions)
    return _question_to_response(next_q, total)


@router.post("/{interview_id}/answer")
async def submit_answer(
    interview_id: int,
    payload: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an answer for the current question and receive immediate feedback."""
    interview = _get_interview_or_404(interview_id, current_user, db)

    if interview.status != InterviewStatusEnum.in_progress:
        raise HTTPException(status_code=400, detail="Interview is not in progress.")

    current_q = _next_unanswered_question(interview)
    if not current_q:
        raise HTTPException(status_code=400, detail="All questions already answered.")

    # Build question dict for evaluator
    question_dict = {
        "question_text": current_q.question_text,
        "question_type": current_q.question_type,
        "expected_answer_points": current_q.expected_answer_points or [],
    }

    # Get student data for AI context
    student_data = _get_student_profile_data(current_user, db)
    eval_result = await evaluate_answer(
        question=question_dict,
        answer_text=payload.answer_text,
        student_profile=student_data,
    )

    # Save answer
    answer = InterviewAnswer(
        question_id=current_q.id,
        interview_id=interview_id,
        answer_text=payload.answer_text,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        strengths=eval_result.get("strengths", []),
        weaknesses=eval_result.get("weaknesses", []),
        better_answer_example=eval_result.get("better_answer_example"),
        technical_correctness=eval_result.get("technical_correctness"),
        relevance=eval_result.get("relevance"),
        communication_quality=eval_result.get("communication_quality"),
        completeness=eval_result.get("completeness"),
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Refresh interview to get updated questions
    db.refresh(interview)
    next_q = _next_unanswered_question(interview)
    total = len(interview.questions)

    return _answer_to_response(answer, next_q, total)


@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete the interview: calculate scores, generate improvement areas."""
    interview = _get_interview_or_404(interview_id, current_user, db)

    if interview.status == InterviewStatusEnum.completed:
        raise HTTPException(status_code=400, detail="Interview already completed.")

    # Collect answered questions
    answers_with_questions = []
    for q in interview.questions:
        if q.answer:
            question_dict = {
                "question_type": q.question_type,
                "topic": q.topic,
                "expected_answer_points": q.expected_answer_points or [],
            }
            answer_dict = {
                "score": q.answer.score,
                "technical_correctness": q.answer.technical_correctness,
                "relevance": q.answer.relevance,
                "communication_quality": q.answer.communication_quality,
                "completeness": q.answer.completeness,
            }
            answers_with_questions.append((question_dict, answer_dict))

    if not answers_with_questions:
        raise HTTPException(status_code=400, detail="No answers submitted yet.")

    # Generate feedback
    feedback = await generate_feedback(
        answers_with_questions=answers_with_questions,
        career=interview.target_career,
        interview_type=interview.interview_type.value,
    )

    # Update interview
    interview.status = InterviewStatusEnum.completed
    interview.completed_at = datetime.utcnow()
    interview.overall_score = feedback.get("overall_score")
    interview.technical_score = feedback.get("technical_score")
    interview.communication_score = feedback.get("communication_score")
    interview.relevance_score = feedback.get("relevance_score")
    interview.problem_solving_score = feedback.get("problem_solving_score")
    interview.project_knowledge_score = feedback.get("project_knowledge_score")
    interview.hr_behavioral_score = feedback.get("hr_behavioral_score")
    interview.technical_accuracy_score = feedback.get("technical_accuracy_score")
    interview.feedback_summary = feedback.get("feedback_summary")
    interview.improvement_areas = [imp["area"] for imp in feedback.get("improvements", [])]

    # Save improvement records
    db.query(InterviewImprovement).filter(
        InterviewImprovement.interview_id == interview_id
    ).delete()

    for imp in feedback.get("improvements", []):
        improvement = InterviewImprovement(
            interview_id=interview_id,
            priority=PriorityEnum(imp["priority"]),
            area=imp["area"],
            topic=imp.get("topic"),
            explanation=imp.get("explanation"),
            practice_suggestion=imp.get("practice_suggestion"),
            learning_resource_url=imp.get("learning_resource_url"),
        )
        db.add(improvement)

    # Update interview readiness score on profile
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if profile and feedback.get("overall_score") is not None:
        profile.interview_readiness_score = feedback["overall_score"]
        # Recompute overall_score
        scores = [
            profile.ats_score or 0,
            profile.skill_match_score or 0,
            profile.career_match_score or 0,
            profile.job_match_score or 0,
            profile.interview_readiness_score or 0,
        ]
        profile.overall_score = round(sum(scores) / len(scores), 1)

    db.commit()
    db.refresh(interview)

    return _build_complete_response(interview)


@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full interview detail: all questions + answers + scores."""
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == current_user.id)
        .options(
            joinedload(Interview.questions).joinedload(InterviewQuestion.answer),
            joinedload(Interview.improvements),
        )
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return _build_complete_response(interview)


@router.get("/{interview_id}/improvements")
def get_improvements(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get improvement recommendations for a completed interview."""
    interview = _get_interview_or_404(interview_id, current_user, db)
    return [
        {
            "id": imp.id,
            "interview_id": imp.interview_id,
            "priority": imp.priority,
            "area": imp.area,
            "topic": imp.topic,
            "explanation": imp.explanation,
            "practice_suggestion": imp.practice_suggestion,
            "learning_resource_url": imp.learning_resource_url,
            "example_better_answer": imp.example_better_answer,
        }
        for imp in interview.improvements
    ]


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Abandon/delete an interview."""
    interview = _get_interview_or_404(interview_id, current_user, db)
    db.delete(interview)
    db.commit()


# ── Builder helpers ───────────────────────────────────────────────────────────

def _build_complete_response(interview: Interview) -> dict:
    questions_out = []
    for q in interview.questions:
        ans = None
        if q.answer:
            ans = {
                "id": q.answer.id,
                "question_id": q.answer.question_id,
                "interview_id": q.answer.interview_id,
                "score": q.answer.score,
                "feedback": q.answer.feedback,
                "strengths": q.answer.strengths or [],
                "weaknesses": q.answer.weaknesses or [],
                "better_answer_example": q.answer.better_answer_example,
                "technical_correctness": q.answer.technical_correctness,
                "relevance": q.answer.relevance,
                "communication_quality": q.answer.communication_quality,
                "completeness": q.answer.completeness,
            }
        questions_out.append({
            "id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "answer": ans,
        })

    improvements_out = [
        {
            "id": imp.id,
            "interview_id": imp.interview_id,
            "priority": imp.priority,
            "area": imp.area,
            "topic": imp.topic,
            "explanation": imp.explanation,
            "practice_suggestion": imp.practice_suggestion,
            "learning_resource_url": imp.learning_resource_url,
            "example_better_answer": imp.example_better_answer,
        }
        for imp in interview.improvements
    ]

    return {
        "id": interview.id,
        "user_id": interview.user_id,
        "target_career": interview.target_career,
        "target_role": interview.target_role,
        "interview_type": interview.interview_type,
        "difficulty": interview.difficulty,
        "status": interview.status,
        "overall_score": interview.overall_score,
        "technical_score": interview.technical_score,
        "communication_score": interview.communication_score,
        "relevance_score": interview.relevance_score,
        "problem_solving_score": interview.problem_solving_score,
        "project_knowledge_score": interview.project_knowledge_score,
        "hr_behavioral_score": interview.hr_behavioral_score,
        "technical_accuracy_score": interview.technical_accuracy_score,
        "feedback_summary": interview.feedback_summary,
        "improvement_areas": interview.improvement_areas,
        "created_at": interview.created_at,
        "completed_at": interview.completed_at,
        "questions": questions_out,
        "improvements": improvements_out,
    }
