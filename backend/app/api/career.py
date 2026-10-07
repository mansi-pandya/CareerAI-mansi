"""
Career API router — all /api/career endpoints.
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.career import (
    Career, CareerMatch, SkillGap, LearningResource,
    LearningRoadmap, LearningProgress,
)
from app.models.profile import StudentProfile, StudentSkill, Education, Skill, CareerPreference
from app.schemas.career import (
    CareerResponse, CareerListItem, CareerMatchResponse,
    SkillGapResponse, LearningResourceResponse,
    LearningRoadmapResponse, LearningProgressCreate, LearningProgressResponse,
    WhatIfResponse,
)
from app.career.recommender import recommender, CAREER_PROFILES
from app.career.skill_gap import analyze_skill_gap, simulate_skill_addition
from app.career.learning import get_resources_for_skill, get_all_resources
from app.career.roadmap import generate_roadmap

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_student_data(user: User, db: Session):
    """Return (profile, student_skills, education, preferences) for the current user."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        return None, [], [], []

    student_skills_raw = (
        db.query(StudentSkill)
        .filter(StudentSkill.profile_id == profile.id)
        .join(Skill)
        .all()
    )
    student_skills = [
        {"name": ss.skill.name, "proficiency": ss.proficiency}
        for ss in student_skills_raw
    ]

    education_raw = db.query(Education).filter(Education.profile_id == profile.id).all()
    education = [
        {
            "degree": e.degree,
            "field_of_study": e.field_of_study,
            "gpa": e.gpa,
            "is_current": e.is_current,
        }
        for e in education_raw
    ]

    prefs_raw = db.query(CareerPreference).filter(CareerPreference.profile_id == profile.id).all()
    preferences = [p.career_title for p in prefs_raw]

    return profile, student_skills, education, preferences


def _career_db_to_response(c: Career, db_match: Optional[CareerMatch] = None) -> dict:
    base = {
        "id": c.id,
        "career_id": c.id,
        "career_name": c.name,
        "career_slug": c.slug,
        "career_industry": c.industry,
        "career_description": c.description,
        "avg_salary_min": c.avg_salary_min,
        "avg_salary_max": c.avg_salary_max,
        "market_demand_score": c.market_demand_score,
        "growth_rate": c.growth_rate,
    }
    if db_match:
        base.update({
            "match_score": db_match.match_score,
            "skill_score": db_match.skill_score,
            "education_score": db_match.education_score,
            "project_score": db_match.project_score,
            "experience_score": db_match.experience_score,
            "interest_score": db_match.interest_score,
            "matched_skills": db_match.matched_skills or [],
            "missing_skills": db_match.missing_skills or [],
            "reasoning": db_match.reasoning,
            "created_at": db_match.created_at,
        })
    return base


# ── Recommendations ───────────────────────────────────────────────────────────

def _compute_and_save_recommendations(user: User, db: Session) -> List[dict]:
    profile, student_skills, education, preferences = _get_student_data(user, db)

    results = recommender.recommend(
        student_skills=student_skills,
        education=education,
        projects=[],
        experience=[],
        career_preferences=preferences,
        preferred_career=profile.preferred_career if profile else None,
    )

    # Delete old matches
    db.query(CareerMatch).filter(CareerMatch.user_id == user.id).delete()

    response_list = []
    for result in results:
        career = db.query(Career).filter(Career.slug == result.career_slug).first()
        if not career:
            continue

        match = CareerMatch(
            user_id=user.id,
            career_id=career.id,
            match_score=result.match_score,
            skill_score=result.skill_score,
            education_score=result.education_score,
            project_score=result.project_score,
            experience_score=result.experience_score,
            interest_score=result.interest_score,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
            reasoning=result.reasoning,
        )
        db.add(match)
        db.flush()

        response_list.append({
            **_career_db_to_response(career, match),
            "id": match.id,
            "created_at": match.created_at,
        })

    db.commit()
    return response_list


@router.get("/recommendations", response_model=List[dict])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get career recommendations for the current user. Computes if not cached."""
    existing = (
        db.query(CareerMatch)
        .filter(CareerMatch.user_id == current_user.id)
        .join(Career)
        .all()
    )
    if existing:
        return [
            {**_career_db_to_response(m.career, m), "id": m.id, "created_at": m.created_at}
            for m in existing
        ]
    return _compute_and_save_recommendations(current_user, db)


@router.post("/recommendations/refresh", response_model=List[dict])
def refresh_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recalculate career recommendations from latest profile data."""
    return _compute_and_save_recommendations(current_user, db)


# ── Careers ───────────────────────────────────────────────────────────────────

@router.get("/careers", response_model=List[CareerListItem])
def list_careers(db: Session = Depends(get_db)):
    """List all available career profiles."""
    careers = db.query(Career).all()
    return careers


@router.get("/careers/{slug}")
def get_career(slug: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific career."""
    career = db.query(Career).filter(Career.slug == slug).first()
    if not career:
        raise HTTPException(status_code=404, detail=f"Career '{slug}' not found")
    return {
        "id": career.id,
        "name": career.name,
        "slug": career.slug,
        "description": career.description,
        "industry": career.industry,
        "required_skills": career.required_skills or [],
        "preferred_skills": career.preferred_skills or [],
        "education_requirements": career.education_requirements or {},
        "market_demand_score": career.market_demand_score,
        "avg_salary_min": career.avg_salary_min,
        "avg_salary_max": career.avg_salary_max,
        "growth_rate": career.growth_rate,
    }


# ── Skill Gap ─────────────────────────────────────────────────────────────────

@router.get("/skill-gap/{career_slug}")
def get_skill_gap(
    career_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get skill gap analysis between student's current skills and target career."""
    profile, student_skills, _, _ = _get_student_data(current_user, db)
    gap = analyze_skill_gap(career_slug, student_skills)
    if "error" in gap:
        raise HTTPException(status_code=404, detail=gap["error"])

    # Persist/update SkillGap records
    db.query(SkillGap).filter(
        SkillGap.user_id == current_user.id,
    ).filter(
        SkillGap.career_id == db.query(Career).filter(Career.slug == career_slug).first().id
        if db.query(Career).filter(Career.slug == career_slug).first() else 0
    ).delete()

    career = db.query(Career).filter(Career.slug == career_slug).first()
    if career:
        for item in gap["missing_skills"]:
            sg = SkillGap(
                user_id=current_user.id,
                career_id=career.id,
                skill_name=item["skill_name"],
                importance=item["importance"],
                current_level=item["current_level"],
                required_level=item["required_level"],
                gap=item["gap"],
                priority=item["priority"],
            )
            db.add(sg)
        db.commit()

    return gap


# ── Learning Resources ────────────────────────────────────────────────────────

@router.get("/learning-resources")
def get_learning_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get learning resources for user's current skill gaps."""
    _, student_skills, _, _ = _get_student_data(current_user, db)
    student_skill_names = {s["name"].lower() for s in student_skills}

    gaps = (
        db.query(SkillGap)
        .filter(SkillGap.user_id == current_user.id)
        .all()
    )

    # Unique missing skills across all careers
    missing = {}
    for g in gaps:
        key = g.skill_name.lower()
        if key not in missing or g.importance == "critical":
            missing[key] = {
                "skill_name": g.skill_name,
                "importance": g.importance,
                "priority": g.priority,
            }

    # Fallback: use full resource list if no gaps tracked yet
    if not missing:
        return get_all_resources()

    result = []
    for skill_data in missing.values():
        skill = skill_data["skill_name"]
        resources = get_resources_for_skill(skill, max_resources=2)
        for r in resources:
            result.append({**r, "importance": skill_data["importance"]})

    return result


@router.get("/learning-resources/{skill}")
def get_resources_for_specific_skill(
    skill: str,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get learning resources for a specific skill."""
    resources = get_resources_for_skill(skill, max_resources=5, preferred_difficulty=difficulty)
    return resources


# ── Learning Progress ─────────────────────────────────────────────────────────

@router.post("/learning-progress", response_model=LearningProgressResponse)
def update_learning_progress(
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update or create learning progress for a skill."""
    progress = (
        db.query(LearningProgress)
        .filter(
            LearningProgress.user_id == current_user.id,
            LearningProgress.skill_name == data.skill_name,
        )
        .first()
    )
    if progress:
        progress.proficiency_level = data.proficiency_level
        progress.notes = data.notes
    else:
        progress = LearningProgress(
            user_id=current_user.id,
            skill_name=data.skill_name,
            proficiency_level=data.proficiency_level,
            notes=data.notes,
        )
        db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/learning-progress", response_model=List[LearningProgressResponse])
def get_learning_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all learning progress entries for the current user."""
    return (
        db.query(LearningProgress)
        .filter(LearningProgress.user_id == current_user.id)
        .all()
    )


# ── Roadmap ───────────────────────────────────────────────────────────────────

@router.get("/roadmap/{career_slug}")
def get_roadmap(
    career_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the learning roadmap for a career. Returns cached if available."""
    career = db.query(Career).filter(Career.slug == career_slug).first()
    if not career:
        raise HTTPException(status_code=404, detail=f"Career '{career_slug}' not found")

    existing = (
        db.query(LearningRoadmap)
        .filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.career_id == career.id,
        )
        .first()
    )

    _, student_skills, _, _ = _get_student_data(current_user, db)

    if existing:
        return {
            "id": existing.id,
            "career_id": existing.career_id,
            "career_name": career.name,
            "career_slug": career.slug,
            "title": existing.title,
            "phases": existing.phases,
            "created_at": existing.created_at,
            "updated_at": existing.updated_at,
        }

    return _generate_and_save_roadmap(career_slug, career, student_skills, current_user.id, db)


@router.post("/roadmap/{career_slug}/generate")
def generate_roadmap_endpoint(
    career_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate or regenerate the learning roadmap for a career."""
    career = db.query(Career).filter(Career.slug == career_slug).first()
    if not career:
        raise HTTPException(status_code=404, detail=f"Career '{career_slug}' not found")

    _, student_skills, _, _ = _get_student_data(current_user, db)

    # Delete existing roadmap
    db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == current_user.id,
        LearningRoadmap.career_id == career.id,
    ).delete()
    db.commit()

    return _generate_and_save_roadmap(career_slug, career, student_skills, current_user.id, db)


def _generate_and_save_roadmap(career_slug, career, student_skills, user_id, db):
    roadmap_data = generate_roadmap(career_slug, student_skills, user_id, career.id)
    if "error" in roadmap_data:
        raise HTTPException(status_code=404, detail=roadmap_data["error"])

    roadmap = LearningRoadmap(
        user_id=user_id,
        career_id=career.id,
        title=roadmap_data["title"],
        phases=roadmap_data["phases"],
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    return {
        **roadmap_data,
        "id": roadmap.id,
        "created_at": roadmap.created_at,
        "updated_at": roadmap.updated_at,
    }


# ── What-If Simulation ────────────────────────────────────────────────────────

@router.get("/what-if")
def what_if_simulation(
    career_slug: str = Query(..., description="Career slug to evaluate"),
    skills: str = Query(..., description="Comma-separated skill names to simulate learning"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simulate: 'If I learn these skills, how much will my career match improve?'
    Returns current_match, estimated_match, and explanation.
    """
    career = db.query(Career).filter(Career.slug == career_slug).first()
    if not career:
        raise HTTPException(status_code=404, detail=f"Career '{career_slug}' not found")

    _, student_skills, _, _ = _get_student_data(current_user, db)
    new_skills = [s.strip() for s in skills.split(",") if s.strip()]

    # Get current match score
    existing_match = (
        db.query(CareerMatch)
        .filter(CareerMatch.user_id == current_user.id, CareerMatch.career_id == career.id)
        .first()
    )
    current_match = existing_match.match_score if existing_match else 0.0

    result = simulate_skill_addition(career_slug, student_skills, new_skills, current_match)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        **result,
        "disclaimer": (
            "This is an estimated projection based on skill weights. "
            "Actual career outcomes depend on many factors beyond this score."
        ),
    }
