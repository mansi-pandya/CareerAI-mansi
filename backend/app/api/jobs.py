"""
Jobs API router — all /api/jobs endpoints.
"""
from __future__ import annotations

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.jobs import Job, JobMatch, SavedJob, SavedJobStatusEnum, JobSource
from app.models.profile import StudentProfile, StudentSkill, Skill
from app.jobs.aggregator import fetch_and_store_jobs, get_jobs_from_db
from app.jobs.matcher import compute_matches_for_user, get_match_for_job, score_job, _build_student_context
from app.jobs.market_analysis import get_skill_demand, get_market_trends

router = APIRouter()

# ── Per-user rate-limit store for /refresh (1 per minute) ───────────────────
_refresh_rate: dict[int, float] = {}

_optional_bearer = HTTPBearer(auto_error=False)


def _get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return current user if authenticated, else None."""
    if not credentials:
        return None
    try:
        from app.core.security import decode_token
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user if (user and user.is_active) else None
    except Exception:
        return None


def _job_to_dict(job: Job, match: Optional[dict] = None, user_saved_ids: Optional[set] = None) -> dict:
    source = job.source
    d = {
        "id": job.id,
        "external_id": job.external_id,
        "source_id": job.source_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "city": job.city,
        "state": job.state,
        "country": job.country,
        "job_type": job.job_type.value if job.job_type else None,
        "work_mode": job.work_mode.value if job.work_mode else None,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "experience_min_years": job.experience_min_years,
        "experience_max_years": job.experience_max_years,
        "required_skills": job.required_skills or [],
        "description": job.description,
        "application_url": job.application_url,
        "source_url": job.source_url,
        "posted_date": job.posted_date.isoformat() if job.posted_date else None,
        "expires_date": job.expires_date.isoformat() if job.expires_date else None,
        "is_active": job.is_active,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "source_name": source.name if source else None,
        "source_slug": source.slug if source else None,
        "is_demo": (source.slug == "demo") if source else False,
        "is_saved": (job.id in user_saved_ids) if user_saved_ids is not None else False,
    }
    if match:
        d.update({
            "overall_score": match.get("overall_score"),
            "skill_score": match.get("skill_score"),
            "role_score": match.get("role_score"),
            "education_score": match.get("education_score"),
            "experience_score": match.get("experience_score"),
            "location_score": match.get("location_score"),
            "preference_score": match.get("preference_score"),
            "match_reasons": match.get("match_reasons", []),
        })
    return d


# ── Search ────────────────────────────────────────────────────────────────────

@router.get("/search")
def search_jobs(
    keywords: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    work_mode: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    skills: Optional[str] = Query(None, description="Comma-separated skill names"),
    salary_min: Optional[int] = Query(None),
    salary_max: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("newest"),
    current_user: Optional[User] = Depends(_get_optional_user),
    db: Session = Depends(get_db),
):
    skills_list = [s.strip() for s in skills.split(",")] if skills else None

    # If no jobs in DB yet, trigger a fetch
    total_jobs = db.query(Job).count()
    if total_jobs == 0:
        fetch_and_store_jobs(
            db,
            keywords=keywords or "",
            location=location or "",
            job_type=job_type,
            work_mode=work_mode,
            limit=50,
            source_filter=source,
        )

    jobs, total = get_jobs_from_db(
        db,
        keywords=keywords,
        job_type=job_type,
        work_mode=work_mode,
        location=location,
        skills=skills_list,
        salary_min=salary_min,
        salary_max=salary_max,
        company=company,
        source=source,
        page=page,
        limit=limit,
        sort_by=sort_by,
    )

    # Collect user's saved job IDs
    saved_ids: set = set()
    match_map: dict = {}
    if current_user:
        saved_rows = db.query(SavedJob.job_id).filter(SavedJob.user_id == current_user.id).all()
        saved_ids = {r[0] for r in saved_rows}

        existing_matches = (
            db.query(JobMatch)
            .filter(JobMatch.user_id == current_user.id)
            .all()
        )
        match_map = {m.job_id: m for m in existing_matches}

    result_jobs = []
    has_demo = False
    for job in jobs:
        match_data = None
        if current_user:
            if job.id in match_map:
                m = match_map[job.id]
                match_data = {
                    "overall_score": m.overall_score,
                    "skill_score": m.skill_score,
                    "role_score": m.role_score,
                    "education_score": m.education_score,
                    "experience_score": m.experience_score,
                    "location_score": m.location_score,
                    "preference_score": m.preference_score,
                    "match_reasons": m.match_reasons or [],
                }
        d = _job_to_dict(job, match_data, saved_ids)
        if d.get("is_demo"):
            has_demo = True
        result_jobs.append(d)

    # Sort by match score if requested
    if sort_by == "match" and current_user:
        result_jobs.sort(key=lambda j: j.get("overall_score") or 0, reverse=True)

    return {
        "jobs": result_jobs,
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": (page * limit) < total,
        "has_demo": has_demo,
    }


# ── Match ─────────────────────────────────────────────────────────────────────

@router.post("/match")
def trigger_match(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Queue match computation for the current user (runs in background)."""
    def _run(user_id: int):
        from app.database.database import SessionLocal
        s = SessionLocal()
        try:
            compute_matches_for_user(user_id, s)
        finally:
            s.close()

    background_tasks.add_task(_run, current_user.id)
    return {"message": "Match computation started", "status": "queued"}


@router.get("/recommended")
def get_recommended(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return top job matches for the current user."""
    matches = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id)
        .order_by(JobMatch.overall_score.desc())
        .limit(limit)
        .all()
    )
    if not matches:
        # Compute on the fly
        compute_matches_for_user(current_user.id, db)
        matches = (
            db.query(JobMatch)
            .filter(JobMatch.user_id == current_user.id)
            .order_by(JobMatch.overall_score.desc())
            .limit(limit)
            .all()
        )

    saved_rows = db.query(SavedJob.job_id).filter(SavedJob.user_id == current_user.id).all()
    saved_ids = {r[0] for r in saved_rows}

    result = []
    for m in matches:
        job = m.job
        if not job or not job.is_active:
            continue
        match_data = {
            "overall_score": m.overall_score,
            "skill_score": m.skill_score,
            "role_score": m.role_score,
            "education_score": m.education_score,
            "experience_score": m.experience_score,
            "location_score": m.location_score,
            "preference_score": m.preference_score,
            "match_reasons": m.match_reasons or [],
        }
        result.append(_job_to_dict(job, match_data, saved_ids))

    return result


# ── Saved Jobs ────────────────────────────────────────────────────────────────

@router.get("/saved")
def get_saved_jobs(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SavedJob).filter(SavedJob.user_id == current_user.id)
    if status:
        try:
            st = SavedJobStatusEnum(status)
            query = query.filter(SavedJob.status == st)
        except ValueError:
            pass
    saved_rows = query.order_by(SavedJob.saved_at.desc()).all()

    saved_ids = {r.job_id for r in saved_rows}

    result = []
    for s in saved_rows:
        job = s.job
        if not job:
            continue
        d = _job_to_dict(job, None, saved_ids)
        d["saved_id"] = s.id
        d["saved_status"] = s.status.value
        d["saved_notes"] = s.notes
        d["saved_at"] = s.saved_at.isoformat() if s.saved_at else None
        d["applied_at"] = s.applied_at.isoformat() if s.applied_at else None
        result.append(d)

    return result


@router.post("/save/{job_id}")
def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
        .first()
    )
    if existing:
        return {"message": "Job already saved", "id": existing.id}

    saved = SavedJob(
        user_id=current_user.id,
        job_id=job_id,
        status=SavedJobStatusEnum.saved,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"message": "Job saved", "id": saved.id}


@router.delete("/save/{job_id}")
def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(saved)
    db.commit()
    return {"message": "Job removed from saved"}


@router.put("/save/{job_id}/status")
def update_saved_status(
    job_id: int,
    status: str,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")

    try:
        saved.status = SavedJobStatusEnum(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if notes is not None:
        saved.notes = notes
    if status == "applied":
        from datetime import datetime
        saved.applied_at = datetime.utcnow()

    db.commit()
    return {"message": "Status updated", "status": saved.status.value}


# ── Market Analysis ───────────────────────────────────────────────────────────

@router.get("/market/skills")
def market_skills(
    current_user: Optional[User] = Depends(_get_optional_user),
    db: Session = Depends(get_db),
):
    user_skills: List[str] = []
    if current_user:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if profile:
            raw = (
                db.query(StudentSkill)
                .filter(StudentSkill.profile_id == profile.id)
                .join(Skill)
                .all()
            )
            user_skills = [ss.skill.name for ss in raw]

    return get_skill_demand(db, user_skills=user_skills, top_n=20)


@router.get("/market/trends")
def market_trends(db: Session = Depends(get_db)):
    return get_market_trends(db)


# ── Job Detail (must be LAST GET to avoid shadowing literal routes) ───────────

@router.get("/{job_id}")
def get_job(
    job_id: int,
    current_user: Optional[User] = Depends(_get_optional_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    saved_ids: set = set()
    match_data = None
    if current_user:
        saved_rows = db.query(SavedJob.job_id).filter(SavedJob.user_id == current_user.id).all()
        saved_ids = {r[0] for r in saved_rows}
        match_data = get_match_for_job(current_user.id, job, db)

    # Similar jobs: same work mode or overlapping skills, limit 4
    similar = (
        db.query(Job)
        .filter(Job.id != job_id, Job.is_active == True)
        .filter(Job.work_mode == job.work_mode)
        .limit(4)
        .all()
    )
    similar_list = [_job_to_dict(j, None, saved_ids) for j in similar]

    result = _job_to_dict(job, match_data, saved_ids)
    result["similar_jobs"] = similar_list
    return result


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh")
def refresh_jobs(
    keywords: str = Query("software developer"),
    location: str = Query("India"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a fresh job fetch from all providers. Rate-limited: 1 per minute per user."""
    now = time.time()
    last = _refresh_rate.get(current_user.id, 0)
    if now - last < 60:
        raise HTTPException(
            status_code=429,
            detail="Please wait 1 minute between job refreshes.",
        )
    _refresh_rate[current_user.id] = now

    fetch_and_store_jobs(db, keywords=keywords, location=location, limit=50)
    total = db.query(Job).count()
    return {"message": "Job refresh complete", "total_jobs": total}
