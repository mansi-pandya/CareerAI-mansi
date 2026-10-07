from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.models.profile import StudentProfile, Education, Skill, StudentSkill, CareerPreference
from app.auth.dependencies import get_current_user
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    EducationCreate,
    EducationResponse,
    StudentSkillCreate,
    StudentSkillResponse,
    CareerPreferenceCreate,
    CareerPreferenceResponse,
)

router = APIRouter()


def _get_or_create_profile(user: User, db: Session) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _compute_profile_completeness(profile: StudentProfile) -> bool:
    required = [profile.college, profile.degree, profile.graduation_year, profile.preferred_career]
    return all(required)


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.is_profile_complete = _compute_profile_completeness(profile)
    db.commit()
    db.refresh(profile)
    return profile


# --- Education ---

@router.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def add_education(
    payload: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    edu = Education(profile_id=profile.id, **payload.model_dump())
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    edu = db.query(Education).filter(
        Education.id == education_id,
        Education.profile_id == profile.id,
    ).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education record not found")
    db.delete(edu)
    db.commit()


# --- Skills ---

@router.post("/skills", response_model=StudentSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    payload: StudentSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)

    # Get or create the skill
    skill = db.query(Skill).filter(Skill.name == payload.skill_name).first()
    if not skill:
        skill = Skill(name=payload.skill_name)
        db.add(skill)
        db.flush()

    # Check if already added
    existing = db.query(StudentSkill).filter(
        StudentSkill.profile_id == profile.id,
        StudentSkill.skill_id == skill.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill already added")

    student_skill = StudentSkill(
        profile_id=profile.id,
        skill_id=skill.id,
        proficiency=payload.proficiency,
        years_experience=payload.years_experience,
    )
    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)
    return student_skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    student_skill = db.query(StudentSkill).filter(
        StudentSkill.id == skill_id,
        StudentSkill.profile_id == profile.id,
    ).first()
    if not student_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(student_skill)
    db.commit()


# --- Career Preferences ---

@router.post("/career-preferences", response_model=CareerPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def add_career_preference(
    payload: CareerPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    pref = CareerPreference(profile_id=profile.id, **payload.model_dump())
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


@router.delete("/career-preferences/{pref_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_career_preference(
    pref_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(current_user, db)
    pref = db.query(CareerPreference).filter(
        CareerPreference.id == pref_id,
        CareerPreference.profile_id == profile.id,
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(pref)
    db.commit()
