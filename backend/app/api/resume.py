"""
Resume API Router — /api/resume/*
"""
import os
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ResumeSection, SectionType
from app.schemas.resume import (
    ResumeResponse,
    ResumeDetailResponse,
    ResumeVersionResponse,
    ResumeUploadResponse,
    ResumeBuilderRequest,
    ResumeUpdate,
    AIImproveRequest,
    AIImproveResponse,
    ParsedResumeData,
)
from app.resume.parser import parse_resume
from app.core.config import settings

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_file(file: UploadFile) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed.",
        )


def _get_resume_or_404(resume_id: int, user_id: int, db: Session) -> Resume:
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == user_id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


def _parsed_data_to_sections(resume_id: int, parsed: dict) -> list:
    """Convert parsed resume dict to ResumeSection ORM objects."""
    mapping = {
        SectionType.contact: parsed.get("contact") or {},
        SectionType.education: {"items": parsed.get("education") or []},
        SectionType.skills: parsed.get("skills") or {},
        SectionType.projects: {"items": parsed.get("projects") or []},
        SectionType.experience: {"items": parsed.get("experience") or []},
        SectionType.certifications: {"items": parsed.get("certifications") or []},
        SectionType.achievements: {"items": parsed.get("achievements") or []},
        SectionType.summary: {"text": parsed.get("summary") or ""},
    }
    order_map = {
        SectionType.contact: 0,
        SectionType.summary: 1,
        SectionType.education: 2,
        SectionType.skills: 3,
        SectionType.experience: 4,
        SectionType.projects: 5,
        SectionType.certifications: 6,
        SectionType.achievements: 7,
    }
    sections = []
    for stype, content in mapping.items():
        sections.append(ResumeSection(
            resume_id=resume_id,
            section_type=stype,
            content=content,
            order_index=order_map.get(stype, 99),
        ))
    return sections


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(default="My Resume"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a PDF or DOCX resume, parse it, and store the result."""
    _validate_file(file)

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File exceeds the 5 MB size limit.",
        )
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded.")

    try:
        parsed = parse_resume(file_bytes, file.filename or "resume.pdf")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {str(exc)}",
        )

    raw_text = parsed.pop("_raw_text", "")

    # Create Resume record
    resume = Resume(user_id=current_user.id, title=title or file.filename or "My Resume")
    db.add(resume)
    db.flush()

    # Create initial version
    version = ResumeVersion(
        resume_id=resume.id,
        version_number=1,
        raw_text=raw_text,
        parsed_data=parsed,
    )
    db.add(version)
    db.flush()

    # Create sections
    for section in _parsed_data_to_sections(resume.id, parsed):
        db.add(section)

    db.commit()
    db.refresh(resume)
    db.refresh(version)

    # Build ParsedResumeData safely
    try:
        parsed_response = ParsedResumeData(**parsed)
    except Exception:
        parsed_response = ParsedResumeData()

    return ResumeUploadResponse(
        resume_id=resume.id,
        version_id=version.id,
        title=resume.title,
        parsed_data=parsed_response,
        raw_text=raw_text[:2000],
        message="Resume uploaded and parsed successfully.",
    )


@router.get("/list", response_model=List[ResumeResponse])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all resumes belonging to the current user."""
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single resume with its sections and versions."""
    return _get_resume_or_404(resume_id, current_user.id, db)


@router.put("/{resume_id}", response_model=ResumeDetailResponse)
def update_resume(
    resume_id: int,
    payload: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update resume title / active status / parsed data."""
    resume = _get_resume_or_404(resume_id, current_user.id, db)

    if payload.title is not None:
        resume.title = payload.title
    if payload.is_active is not None:
        if payload.is_active:
            # Deactivate all others
            db.query(Resume).filter(
                Resume.user_id == current_user.id, Resume.id != resume_id
            ).update({"is_active": False})
        resume.is_active = payload.is_active

    if payload.parsed_data is not None:
        new_parsed = payload.parsed_data.model_dump(exclude_none=True)
        # Get latest version number
        latest = db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == resume_id
        ).order_by(ResumeVersion.version_number.desc()).first()
        next_v = (latest.version_number + 1) if latest else 1
        version = ResumeVersion(
            resume_id=resume.id,
            version_number=next_v,
            parsed_data=new_parsed,
        )
        db.add(version)
        db.flush()
        # Remove old sections and recreate
        db.query(ResumeSection).filter(ResumeSection.resume_id == resume_id).delete()
        for section in _parsed_data_to_sections(resume.id, new_parsed):
            db.add(section)

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a resume and all related data."""
    resume = _get_resume_or_404(resume_id, current_user.id, db)
    db.delete(resume)
    db.commit()


@router.post("/builder", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
def create_from_builder(
    payload: ResumeBuilderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new resume from builder form data."""
    resume = Resume(user_id=current_user.id, title=payload.title)
    db.add(resume)
    db.flush()

    parsed = payload.model_dump(exclude={"title"}, exclude_none=True)

    version = ResumeVersion(
        resume_id=resume.id,
        version_number=1,
        parsed_data=parsed,
    )
    db.add(version)
    db.flush()

    for section in _parsed_data_to_sections(resume.id, parsed):
        db.add(section)

    db.commit()
    db.refresh(resume)
    return resume


@router.get("/{resume_id}/versions", response_model=List[ResumeVersionResponse])
def list_versions(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all versions of a resume."""
    _get_resume_or_404(resume_id, current_user.id, db)
    return (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume_id)
        .order_by(ResumeVersion.version_number.desc())
        .all()
    )


@router.post("/{resume_id}/ai-improve", response_model=AIImproveResponse)
async def ai_improve(
    resume_id: int,
    payload: AIImproveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Improve the writing quality of a specific resume section using an AI model.
    Requires AI_API_KEY to be configured.
    NEVER adds fabricated information — only improves writing of existing text.
    """
    _get_resume_or_404(resume_id, current_user.id, db)

    if not settings.AI_API_KEY:
        return AIImproveResponse(
            section=payload.section,
            field=payload.field,
            original_text=payload.current_text,
            improved_text=payload.current_text,
            message="AI improvement requires AI_API_KEY configuration. Please set AI_API_KEY in your environment.",
        )

    import httpx

    system_prompt = (
        "You are a professional resume editor. "
        "Your ONLY job is to improve the writing quality, clarity, and impact of the provided resume text. "
        "DO NOT invent, add, or fabricate any skills, technologies, companies, dates, metrics, "
        "or certifications that are not already present in the original text. "
        "Return ONLY the improved text with no explanation, no preamble, no markdown."
    )

    user_prompt = (
        f"Improve the following resume text for the '{payload.section}' section, field '{payload.field}'.\n\n"
        f"Original:\n{payload.current_text}\n\n"
        "Return only the improved version."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 500,
                    "temperature": 0.4,
                },
            )
            response.raise_for_status()
            data = response.json()
            improved = data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {exc.response.status_code}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI improvement failed: {str(exc)}",
        )

    return AIImproveResponse(
        section=payload.section,
        field=payload.field,
        original_text=payload.current_text,
        improved_text=improved,
    )
