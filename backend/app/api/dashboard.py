from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database.database import get_db
from app.models.user import User
from app.models.profile import StudentProfile
from app.auth.dependencies import get_current_user

router = APIRouter()

# Recommended careers data (will be AI-driven in Stage 2+)
CAREER_RECOMMENDATIONS = [
    {"title": "Software Engineer", "match": 92, "industry": "Technology", "avg_salary": "$95,000"},
    {"title": "Data Scientist", "match": 85, "industry": "Technology", "avg_salary": "$110,000"},
    {"title": "Product Manager", "match": 78, "industry": "Technology", "avg_salary": "$105,000"},
    {"title": "UX Designer", "match": 71, "industry": "Design", "avg_salary": "$85,000"},
    {"title": "Cloud Architect", "match": 68, "industry": "Technology", "avg_salary": "$130,000"},
]

SKILL_GAPS = [
    {"skill": "System Design", "importance": "High", "resources": 12},
    {"skill": "Machine Learning", "importance": "High", "resources": 24},
    {"skill": "Kubernetes", "importance": "Medium", "resources": 8},
    {"skill": "GraphQL", "importance": "Medium", "resources": 6},
    {"skill": "TypeScript", "importance": "Low", "resources": 15},
]

JOB_RECOMMENDATIONS = [
    {
        "title": "Junior Software Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "match": 88,
        "type": "Full-time",
        "posted": "2 days ago",
    },
    {
        "title": "Data Analyst Intern",
        "company": "DataViz Inc",
        "location": "New York, NY",
        "match": 82,
        "type": "Internship",
        "posted": "1 week ago",
    },
    {
        "title": "Frontend Developer",
        "company": "StartupXYZ",
        "location": "San Francisco, CA",
        "match": 76,
        "type": "Full-time",
        "posted": "3 days ago",
    },
]


@router.get("/")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if not profile:
        # Return empty state for new users
        return {
            "user": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "role": current_user.role.value,
            },
            "scores": {
                "ats_readiness": 0,
                "skill_match": 0,
                "career_match": 0,
                "job_match": 0,
                "interview_readiness": 0,
                "overall": 0,
            },
            "recommended_careers": [],
            "skill_gaps": [],
            "recommended_jobs": [],
            "profile_complete": False,
            "quick_actions": _get_quick_actions(),
        }

    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role.value,
        },
        "scores": {
            "ats_readiness": round(profile.ats_score, 1),
            "skill_match": round(profile.skill_match_score, 1),
            "career_match": round(profile.career_match_score, 1),
            "job_match": round(profile.job_match_score, 1),
            "interview_readiness": round(profile.interview_readiness_score, 1),
            "overall": round(profile.overall_score, 1),
        },
        "recommended_careers": CAREER_RECOMMENDATIONS,
        "skill_gaps": SKILL_GAPS,
        "recommended_jobs": JOB_RECOMMENDATIONS,
        "profile_complete": profile.is_profile_complete,
        "quick_actions": _get_quick_actions(),
    }


def _get_quick_actions() -> List[Dict]:
    return [
        {"id": "create_resume", "label": "Create Resume", "icon": "DocumentPlusIcon", "href": "/resume/create", "color": "blue"},
        {"id": "upload_resume", "label": "Upload Resume", "icon": "ArrowUpTrayIcon", "href": "/resume/upload", "color": "indigo"},
        {"id": "check_ats", "label": "Check ATS Score", "icon": "ChartBarIcon", "href": "/ats", "color": "purple"},
        {"id": "find_jobs", "label": "Find Jobs", "icon": "BriefcaseIcon", "href": "/jobs", "color": "green"},
        {"id": "verify_opportunity", "label": "Verify Opportunity", "icon": "ShieldCheckIcon", "href": "/verify", "color": "teal"},
        {"id": "start_interview", "label": "AI Interview", "icon": "MicrophoneIcon", "href": "/interview", "color": "orange"},
        {"id": "skill_gaps", "label": "Skill Gap Analysis", "icon": "AcademicCapIcon", "href": "/skills", "color": "red"},
    ]


@router.get("/scores")
async def get_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        return {"ats_readiness": 0, "skill_match": 0, "career_match": 0, "job_match": 0, "interview_readiness": 0, "overall": 0}

    return {
        "ats_readiness": round(profile.ats_score, 1),
        "skill_match": round(profile.skill_match_score, 1),
        "career_match": round(profile.career_match_score, 1),
        "job_match": round(profile.job_match_score, 1),
        "interview_readiness": round(profile.interview_readiness_score, 1),
        "overall": round(profile.overall_score, 1),
    }
