"""
Job aggregation service.
Tries each configured provider in order (Adzuna first, then demo),
deduplicates results, and persists new jobs to the DB.
"""
from __future__ import annotations

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.jobs import Job, JobSource
from app.jobs.providers.base import JobData
from app.jobs.providers.adzuna import AdzunaProvider
from app.jobs.providers.demo import DemoProvider

logger = logging.getLogger(__name__)

# Ordered list of providers — real first, demo as fallback
_PROVIDERS = [
    AdzunaProvider(),
    DemoProvider(),
]


def _get_or_create_source(db: Session, slug: str) -> Optional[JobSource]:
    source = db.query(JobSource).filter(JobSource.slug == slug).first()
    return source


def _job_data_to_db(jd: JobData, source: JobSource) -> Job:
    return Job(
        external_id=jd.external_id or None,
        source_id=source.id,
        title=jd.title,
        company=jd.company,
        location=jd.location,
        city=jd.city,
        state=jd.state,
        country=jd.country,
        job_type=jd.job_type,
        work_mode=jd.work_mode,
        salary_min=jd.salary_min,
        salary_max=jd.salary_max,
        salary_currency=jd.salary_currency,
        experience_min_years=jd.experience_min_years,
        experience_max_years=jd.experience_max_years,
        required_skills=jd.required_skills,
        description=jd.description,
        application_url=jd.application_url,
        source_url=jd.source_url,
        posted_date=jd.posted_date,
        dedup_hash=Job.compute_hash(jd.company, jd.title, jd.location),
    )


def _is_duplicate(db: Session, jd: JobData) -> bool:
    """Check for duplicates by hash, external_id, or URL."""
    dedup_hash = Job.compute_hash(jd.company, jd.title, jd.location)
    if db.query(Job).filter(Job.dedup_hash == dedup_hash).first():
        return True
    if jd.external_id:
        if db.query(Job).filter(Job.external_id == jd.external_id).first():
            return True
    if jd.source_url:
        if db.query(Job).filter(Job.source_url == jd.source_url).first():
            return True
    return False


def fetch_and_store_jobs(
    db: Session,
    keywords: str = "",
    location: str = "",
    job_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    limit: int = 30,
    source_filter: Optional[str] = None,
) -> List[Job]:
    """
    Fetch jobs from all available providers, deduplicate, store new ones,
    and return the combined list of Job ORM objects.
    """
    all_job_data: List[JobData] = []
    seen_hashes: set = set()  # in-memory dedup for this batch

    for provider in _PROVIDERS:
        if source_filter and provider.slug != source_filter:
            continue
        if not provider.is_available():
            continue

        source = _get_or_create_source(db, provider.slug)
        if not source or not source.is_active:
            continue

        try:
            fetched = provider.fetch_jobs(
                keywords=keywords,
                location=location,
                job_type=job_type,
                work_mode=work_mode,
                limit=limit,
            )
            logger.info("Provider '%s' returned %d jobs", provider.slug, len(fetched))
        except Exception as exc:
            logger.error("Provider '%s' failed: %s", provider.slug, exc)
            continue

        for jd in fetched:
            h = Job.compute_hash(jd.company, jd.title, jd.location)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            if _is_duplicate(db, jd):
                # Return existing record
                existing = db.query(Job).filter(Job.dedup_hash == h).first()
                if existing:
                    all_job_data.append(jd)
                continue

            # Insert new job
            job_db = _job_data_to_db(jd, source)
            db.add(job_db)
            all_job_data.append(jd)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to commit jobs: %s", exc)

    return all_job_data


def get_jobs_from_db(
    db: Session,
    keywords: Optional[str] = None,
    job_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[List[str]] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    company: Optional[str] = None,
    source: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "newest",
) -> tuple[List[Job], int]:
    """Query jobs from DB with filters. Returns (jobs, total_count)."""
    from sqlalchemy import or_, and_, func
    from app.models.jobs import JobTypeEnum, WorkModeEnum

    query = db.query(Job).filter(Job.is_active == True)

    if keywords:
        kw = f"%{keywords.lower()}%"
        query = query.filter(
            or_(
                func.lower(Job.title).like(kw),
                func.lower(Job.company).like(kw),
                func.lower(Job.description).like(kw),
            )
        )

    if job_type:
        try:
            jt = JobTypeEnum(job_type)
            query = query.filter(Job.job_type == jt)
        except ValueError:
            pass

    if work_mode:
        try:
            wm = WorkModeEnum(work_mode)
            query = query.filter(Job.work_mode == wm)
        except ValueError:
            pass

    if location:
        loc = f"%{location.lower()}%"
        query = query.filter(
            or_(
                func.lower(Job.location).like(loc),
                func.lower(Job.city).like(loc),
                Job.work_mode == WorkModeEnum.remote,
            )
        )

    if company:
        query = query.filter(func.lower(Job.company).like(f"%{company.lower()}%"))

    if salary_min is not None:
        query = query.filter(
            or_(Job.salary_min >= salary_min, Job.salary_max >= salary_min)
        )

    if salary_max is not None:
        query = query.filter(
            or_(Job.salary_max <= salary_max, Job.salary_max.is_(None))
        )

    if source:
        src = db.query(JobSource).filter(JobSource.slug == source).first()
        if src:
            query = query.filter(Job.source_id == src.id)

    if skills:
        # Filter jobs that require any of the given skills (JSON field contains)
        from sqlalchemy import cast, String
        for skill in skills:
            sk = f"%{skill.lower()}%"
            query = query.filter(
                func.lower(cast(Job.required_skills, String)).like(sk)
            )

    total = query.count()

    if sort_by == "salary":
        query = query.order_by(Job.salary_max.desc().nullslast())
    else:
        # Default: newest first
        query = query.order_by(Job.posted_date.desc().nullslast(), Job.created_at.desc())

    offset = (page - 1) * limit
    jobs = query.offset(offset).limit(limit).all()

    return jobs, total
