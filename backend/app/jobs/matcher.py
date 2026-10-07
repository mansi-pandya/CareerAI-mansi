"""
AI job matching — scores jobs against a student profile.

Weights:
  skill_score       40 %
  role_score        20 %
  education_score   15 %
  experience_score  10 %
  location_score    10 %
  preference_score   5 %
"""
from __future__ import annotations

import math
import re
from typing import List, Optional, Dict, Any

from app.models.jobs import Job, JobMatch, WorkModeEnum, JobTypeEnum
from app.models.profile import StudentProfile, StudentSkill, Skill, CareerPreference, Education
from sqlalchemy.orm import Session


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def _skill_overlap(student_skills: List[str], job_skills: List[str]) -> tuple[float, List[str], List[str]]:
    """Return (score 0-1, matched, missing) using case-insensitive substring matching."""
    if not job_skills:
        return 0.5, [], []  # neutral when job has no required skills

    norm_student = {_normalize(s) for s in student_skills}
    matched = []
    missing = []
    for js in job_skills:
        njs = _normalize(js)
        # Match if skill appears as substring in any student skill or vice-versa
        found = any(njs in ns or ns in njs for ns in norm_student)
        if found:
            matched.append(js)
        else:
            missing.append(js)

    score = len(matched) / len(job_skills)
    return score, matched, missing


def _tfidf_similarity(text_a: str, text_b: str) -> float:
    """Very lightweight bag-of-words cosine similarity (no external lib)."""
    if not text_a or not text_b:
        return 0.0
    tokens_a = set(_normalize(text_a).split())
    tokens_b = set(_normalize(text_b).split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    # Cosine with equal tf weights
    return len(intersection) / math.sqrt(len(tokens_a) * len(tokens_b))


_DEGREE_RANK = {
    "phd": 4, "doctorate": 4,
    "master": 3, "mtech": 3, "mba": 3, "m.sc": 3,
    "bachelor": 2, "btech": 2, "b.tech": 2, "be": 2, "b.e": 2, "b.sc": 2, "bsc": 2,
    "diploma": 1, "12th": 1, "hsc": 1,
    "10th": 0, "ssc": 0,
}


def _degree_level(degree_str: Optional[str]) -> int:
    if not degree_str:
        return 1  # assume bachelor level
    d = degree_str.lower()
    for key, rank in _DEGREE_RANK.items():
        if key in d:
            return rank
    return 1


def _education_score(student_education: List[dict], exp_years_min: Optional[float]) -> float:
    """
    Simple heuristic:
    - Internship / entry-level (0-1 yr): any degree is fine → 1.0
    - Junior (1-3 yr): bachelor required → check
    - Mid (3-7 yr): strong degree or experience → 0.8
    - Senior (7+ yr): degree matters less → 0.9
    """
    if not student_education:
        return 0.5

    max_degree = max((_degree_level(e.get("degree")) for e in student_education), default=1)

    if exp_years_min is None or exp_years_min <= 1:
        return 1.0
    elif exp_years_min <= 3:
        return 1.0 if max_degree >= 2 else 0.4
    elif exp_years_min <= 7:
        return 1.0 if max_degree >= 2 else 0.6
    else:
        return 0.9  # senior roles care less about formal education


def _experience_score(
    exp_years_min: Optional[float],
    exp_years_max: Optional[float],
    student_years: float,
) -> float:
    """
    Returns 1.0 if student experience is within range,
    partial score for close misses.
    """
    lo = exp_years_min or 0.0
    hi = exp_years_max or lo + 4.0

    if lo <= student_years <= hi:
        return 1.0
    elif student_years < lo:
        gap = lo - student_years
        return max(0.0, 1.0 - gap * 0.25)
    else:
        # Over-qualified — mild penalty
        gap = student_years - hi
        return max(0.5, 1.0 - gap * 0.1)


def _location_score(
    job: Job,
    profile_location: Optional[str],
    preferred_work_mode: Optional[str],
) -> float:
    if job.work_mode == WorkModeEnum.remote:
        return 1.0

    # Prefer remote/hybrid based on student pref
    if preferred_work_mode:
        pref = preferred_work_mode.lower()
        if pref == "remote" and job.work_mode != WorkModeEnum.remote:
            return 0.4
        if pref == "hybrid" and job.work_mode == WorkModeEnum.on_site:
            return 0.6

    # Location string match
    if profile_location and job.location:
        pl = profile_location.lower()
        jl = job.location.lower()
        if any(tok in jl for tok in pl.split() if len(tok) > 3):
            return 1.0
        return 0.5

    return 0.6


def _preference_score(job: Job, career_preferences: List[str]) -> float:
    """Score based on whether job title aligns with stated career preferences."""
    if not career_preferences:
        return 0.5
    best = max(
        _tfidf_similarity(job.title, pref) for pref in career_preferences
    )
    return min(1.0, best * 3.0)  # amplify small overlaps


# ── Main scorer ───────────────────────────────────────────────────────────────

WEIGHTS = {
    "skill": 0.40,
    "role": 0.20,
    "education": 0.15,
    "experience": 0.10,
    "location": 0.10,
    "preference": 0.05,
}


def score_job(
    job: Job,
    student_skills: List[str],
    student_education: List[dict],
    student_years_experience: float,
    profile_location: Optional[str],
    preferred_career: Optional[str],
    career_preferences: List[str],
    preferred_work_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Score a single job against the student profile.
    Returns dict with all sub-scores, overall_score, match_reasons.
    """
    job_skills: List[str] = job.required_skills or []

    # 1. Skill score
    sk_score, matched_skills, missing_skills = _skill_overlap(student_skills, job_skills)

    # 2. Role score
    role_text = " ".join(filter(None, [preferred_career] + career_preferences))
    rl_score = _tfidf_similarity(job.title, role_text)
    # clamp to meaningful range
    rl_score = min(1.0, rl_score * 4.0)

    # 3. Education score
    ed_score = _education_score(student_education, job.experience_min_years)

    # 4. Experience score
    ex_score = _experience_score(
        job.experience_min_years, job.experience_max_years, student_years_experience
    )

    # 5. Location score
    lo_score = _location_score(job, profile_location, preferred_work_mode)

    # 6. Preference score
    pref_score = _preference_score(job, career_preferences)

    overall = (
        sk_score * WEIGHTS["skill"]
        + rl_score * WEIGHTS["role"]
        + ed_score * WEIGHTS["education"]
        + ex_score * WEIGHTS["experience"]
        + lo_score * WEIGHTS["location"]
        + pref_score * WEIGHTS["preference"]
    )
    overall = round(min(1.0, overall), 4)

    # Build human-readable reasons
    reasons: List[str] = []
    if matched_skills:
        reasons.append(
            f"Your {', '.join(matched_skills[:3])} skill{'s' if len(matched_skills) > 1 else ''} "
            f"match{'es' if len(matched_skills) == 1 else ''} "
            f"{len(matched_skills)} of {len(job_skills)} required skills"
        )
    if job.work_mode == WorkModeEnum.remote:
        reasons.append("Fully remote — work from anywhere")
    elif job.work_mode == WorkModeEnum.hybrid:
        reasons.append("Hybrid schedule available")
    if rl_score > 0.3:
        reasons.append(f"Job title aligns with your career interest in {preferred_career or 'this field'}")
    if ex_score >= 1.0:
        reasons.append("Your experience level matches the job requirements")
    elif ex_score >= 0.7:
        reasons.append("You are close to the required experience level")
    if missing_skills and len(missing_skills) <= 2:
        reasons.append(f"Only {len(missing_skills)} skill gap(s): {', '.join(missing_skills)}")
    if job.salary_min and job.salary_max:
        reasons.append(
            f"Salary range: {job.salary_currency} "
            f"{job.salary_min:,} – {job.salary_max:,}"
        )

    return {
        "overall_score": overall,
        "skill_score": round(sk_score, 4),
        "role_score": round(rl_score, 4),
        "education_score": round(ed_score, 4),
        "experience_score": round(ex_score, 4),
        "location_score": round(lo_score, 4),
        "preference_score": round(pref_score, 4),
        "match_reasons": reasons,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


# ── Batch scoring ─────────────────────────────────────────────────────────────

def _build_student_context(user_id: int, db: Session) -> dict:
    from app.models.profile import StudentProfile

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return {}

    raw_skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.profile_id == profile.id)
        .join(Skill)
        .all()
    )
    student_skills = [ss.skill.name for ss in raw_skills]

    # Estimate years experience from highest years_experience field
    student_years = max((ss.years_experience or 0.0 for ss in raw_skills), default=0.0)

    education_raw = db.query(Education).filter(Education.profile_id == profile.id).all()
    student_education = [
        {"degree": e.degree, "field_of_study": e.field_of_study}
        for e in education_raw
    ]

    prefs = db.query(CareerPreference).filter(CareerPreference.profile_id == profile.id).all()
    career_preferences = [p.career_title for p in prefs]

    return {
        "student_skills": student_skills,
        "student_education": student_education,
        "student_years_experience": student_years,
        "profile_location": profile.location,
        "preferred_career": profile.preferred_career,
        "career_preferences": career_preferences,
        "preferred_work_mode": None,
    }


def compute_matches_for_user(user_id: int, db: Session) -> int:
    """
    Calculate match scores for all active jobs for this user.
    Deletes old matches and inserts new ones.
    Returns count of matches computed.
    """
    ctx = _build_student_context(user_id, db)
    if not ctx:
        return 0

    # Delete existing matches
    db.query(JobMatch).filter(JobMatch.user_id == user_id).delete()

    jobs = db.query(Job).filter(Job.is_active == True).all()
    count = 0
    for job in jobs:
        result = score_job(
            job=job,
            student_skills=ctx["student_skills"],
            student_education=ctx["student_education"],
            student_years_experience=ctx["student_years_experience"],
            profile_location=ctx["profile_location"],
            preferred_career=ctx["preferred_career"],
            career_preferences=ctx["career_preferences"],
            preferred_work_mode=ctx.get("preferred_work_mode"),
        )
        jm = JobMatch(
            user_id=user_id,
            job_id=job.id,
            overall_score=result["overall_score"],
            skill_score=result["skill_score"],
            role_score=result["role_score"],
            education_score=result["education_score"],
            experience_score=result["experience_score"],
            location_score=result["location_score"],
            preference_score=result["preference_score"],
            match_reasons=result["match_reasons"],
        )
        db.add(jm)
        count += 1

    db.commit()
    return count


def get_match_for_job(user_id: int, job: Job, db: Session) -> Optional[Dict[str, Any]]:
    """Get or compute match score for a single job."""
    existing = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == user_id, JobMatch.job_id == job.id)
        .first()
    )
    if existing:
        return {
            "overall_score": existing.overall_score,
            "skill_score": existing.skill_score,
            "role_score": existing.role_score,
            "education_score": existing.education_score,
            "experience_score": existing.experience_score,
            "location_score": existing.location_score,
            "preference_score": existing.preference_score,
            "match_reasons": existing.match_reasons or [],
        }

    ctx = _build_student_context(user_id, db)
    if not ctx:
        return None

    return score_job(
        job=job,
        student_skills=ctx["student_skills"],
        student_education=ctx["student_education"],
        student_years_experience=ctx["student_years_experience"],
        profile_location=ctx["profile_location"],
        preferred_career=ctx["preferred_career"],
        career_preferences=ctx["career_preferences"],
        preferred_work_mode=ctx.get("preferred_work_mode"),
    )
