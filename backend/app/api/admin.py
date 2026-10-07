import os
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.core.config import settings
from app.database.database import get_db
from app.models.career import Career, CareerMatch, SkillGap
from app.models.interviews import Interview
from app.models.jobs import JobSearchLog, JobSource, SavedJob
from app.models.opportunities import OpportunityCheck, VerificationStatusEnum
from app.models.profile import Skill, StudentSkill
from app.models.resume import ATSScore, Resume
from app.models.user import Role, User

router = APIRouter()


@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    career_counts = (
        db.query(Career.name, func.count(CareerMatch.id))
        .join(CareerMatch, CareerMatch.career_id == Career.id)
        .group_by(Career.name)
        .order_by(func.count(CareerMatch.id).desc())
        .limit(10)
        .all()
    )

    skill_counts = Counter()
    for skill_name, count in db.query(StudentSkill.skill_id, func.count(StudentSkill.id)).group_by(StudentSkill.skill_id):
        skill_counts[str(skill_name)] += count
    for skill_name, count in db.query(SkillGap.skill_name, func.count(SkillGap.id)).group_by(SkillGap.skill_name):
        skill_counts[skill_name] += count

    verification_outcomes = {
        status.value: db.query(OpportunityCheck)
        .filter(OpportunityCheck.verification_status == status)
        .count()
        for status in VerificationStatusEnum
    }
    sources = db.query(JobSource).order_by(JobSource.name).all()

    return {
        "total_students": db.query(User).filter(User.role == Role.student).count(),
        "active_users": db.query(User).filter(User.is_active.is_(True)).count(),
        "resume_analyses": db.query(Resume).count(),
        "ats_analyses": db.query(ATSScore).count(),
        "job_searches": db.query(JobSearchLog).count(),
        "saved_jobs": db.query(SavedJob).count(),
        "opportunity_checks": db.query(OpportunityCheck).count(),
        "interview_sessions": db.query(Interview).count(),
        "popular_careers": [
            {"career": name, "count": count} for name, count in career_counts
        ],
        "popular_skills": [
            {"skill": name, "count": count}
            for name, count in skill_counts.most_common(10)
        ],
        "common_skill_gaps": [
            {"skill": name, "count": count}
            for name, count in db.query(SkillGap.skill_name, func.count(SkillGap.id))
            .group_by(SkillGap.skill_name)
            .order_by(func.count(SkillGap.id).desc())
            .limit(10)
        ],
        "verification_outcomes": verification_outcomes,
        "api_status": {
            "ai": "configured" if settings.AI_API_KEY else "demo_mode",
            "job_sources": [
                {
                    "name": source.name,
                    "active": bool(source.is_active),
                    "configured": not source.api_key_env_var or bool(__import__("os").environ.get(source.api_key_env_var)),
                }
                for source in sources
            ],
        },
    }
