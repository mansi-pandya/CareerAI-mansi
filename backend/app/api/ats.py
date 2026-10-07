"""
ATS API Router — /api/ats/*
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ATSScore, ATSRecommendation
from app.schemas.resume import (
    ATSScoreResponse,
    ATSAnalysisRequest,
    ATSRecommendationResponse,
    ATSScoreHistoryItem,
)
from app.ats.analyzer import analyze_resume

router = APIRouter()


def _get_resume_or_404(resume_id: int, user_id: int, db: Session) -> Resume:
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == user_id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


def _get_latest_parsed_data(resume: Resume, db: Session) -> dict:
    """Return the parsed_data dict from the latest version, or an empty dict."""
    latest = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume.id)
        .order_by(ResumeVersion.version_number.desc())
        .first()
    )
    if latest and latest.parsed_data:
        return dict(latest.parsed_data)
    # Fallback: build from sections
    sections = resume.sections
    data: dict = {}
    for sec in sections:
        content = dict(sec.content) if sec.content else {}
        data[sec.section_type.value] = content
    return data


def _run_and_store_analysis(
    resume: Resume,
    parsed_data: dict,
    job_description: Optional[str],
    db: Session,
) -> ATSScore:
    """Run analysis, persist ATSScore + ATSRecommendation rows, and return the score."""
    result = analyze_resume(parsed_data, job_description)

    # Latest version id
    latest_version = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume.id)
        .order_by(ResumeVersion.version_number.desc())
        .first()
    )

    ats_score = ATSScore(
        resume_id=resume.id,
        version_id=latest_version.id if latest_version else None,
        overall_score=result.overall_score,
        structure_score=result.structure_score,
        formatting_score=result.formatting_score,
        keyword_score=result.keyword_score,
        skills_score=result.skills_score,
        projects_score=result.projects_score,
        experience_score=result.experience_score,
        education_score=result.education_score,
        contact_score=result.contact_score,
        job_alignment_score=result.job_alignment_score,
        analysis_data=result.analysis_data,
    )
    db.add(ats_score)
    db.flush()

    for rec_dict in result.recommendations:
        rec = ATSRecommendation(
            ats_score_id=ats_score.id,
            **rec_dict,
        )
        db.add(rec)

    db.commit()
    db.refresh(ats_score)
    return ats_score


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/analyze/{resume_id}", response_model=ATSScoreResponse, status_code=status.HTTP_201_CREATED)
def analyze(
    resume_id: int,
    payload: ATSAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run ATS analysis on a resume and store the result."""
    resume = _get_resume_or_404(resume_id, current_user.id, db)
    parsed_data = _get_latest_parsed_data(resume, db)
    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No parsed data found for this resume. Upload or build a resume first.",
        )
    ats_score = _run_and_store_analysis(resume, parsed_data, payload.job_description, db)
    return ats_score


@router.get("/results/{resume_id}", response_model=ATSScoreResponse)
def get_latest_results(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent ATS analysis result for a resume."""
    _get_resume_or_404(resume_id, current_user.id, db)
    score = (
        db.query(ATSScore)
        .filter(ATSScore.resume_id == resume_id)
        .order_by(ATSScore.created_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=404, detail="No ATS analysis found for this resume. Run an analysis first.")
    return score


@router.get("/history/{resume_id}", response_model=List[ATSScoreHistoryItem])
def get_score_history(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all ATS score records for improvement-loop chart."""
    _get_resume_or_404(resume_id, current_user.id, db)
    scores = (
        db.query(ATSScore)
        .filter(ATSScore.resume_id == resume_id)
        .order_by(ATSScore.created_at.asc())
        .all()
    )
    # Attach version_number from the linked version
    result = []
    for s in scores:
        version_number = s.version.version_number if s.version else None
        result.append(ATSScoreHistoryItem(
            id=s.id,
            version_number=version_number,
            overall_score=s.overall_score,
            structure_score=s.structure_score,
            formatting_score=s.formatting_score,
            keyword_score=s.keyword_score,
            skills_score=s.skills_score,
            projects_score=s.projects_score,
            experience_score=s.experience_score,
            education_score=s.education_score,
            contact_score=s.contact_score,
            job_alignment_score=s.job_alignment_score,
            created_at=s.created_at,
        ))
    return result


@router.post("/analyze-with-job/{resume_id}", response_model=ATSScoreResponse, status_code=status.HTTP_201_CREATED)
def analyze_with_job(
    resume_id: int,
    payload: ATSAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run ATS analysis with a job description for job-specific scoring."""
    if not payload.job_description or not payload.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_description is required for job-specific analysis.",
        )
    resume = _get_resume_or_404(resume_id, current_user.id, db)
    parsed_data = _get_latest_parsed_data(resume, db)
    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No parsed data found. Upload or build a resume first.",
        )
    ats_score = _run_and_store_analysis(resume, parsed_data, payload.job_description, db)
    return ats_score


@router.get("/recommendations/{ats_score_id}", response_model=List[ATSRecommendationResponse])
def get_recommendations(
    ats_score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all recommendations for a specific ATS score record."""
    score = db.query(ATSScore).filter(ATSScore.id == ats_score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="ATS score not found")
    # Verify ownership
    resume = db.query(Resume).filter(
        Resume.id == score.resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=403, detail="Access denied")
    return score.recommendations
