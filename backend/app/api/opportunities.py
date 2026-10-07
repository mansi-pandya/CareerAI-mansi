"""
Opportunities API Router — /api/opportunities/*
"""
import os
import uuid
import shutil
from typing import List

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File,
    Form, status
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.profile import StudentProfile, StudentSkill
from app.models.opportunities import (
    OpportunityCheck, OpportunityDocument,
    InputTypeEnum, VerificationStatusEnum,
)
from app.schemas.opportunities import (
    OpportunityCheckResponse,
    OpportunityCheckListItem,
)
from app.opportunities.extractor import (
    extract_from_text,
    extract_from_url,
    extract_from_image,
    extract_from_pdf,
)
from app.opportunities.verifier import verify_opportunity
from app.opportunities.apply_advisor import compare_opportunity_with_profile

router = APIRouter()

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PDF_TYPE = "application/pdf"
UPLOAD_BASE = "uploads/opportunities"


def _upload_dir(user_id: int) -> str:
    path = os.path.join(UPLOAD_BASE, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def _get_check_or_404(check_id: int, user_id: int, db: Session) -> OpportunityCheck:
    check = db.query(OpportunityCheck).filter(
        OpportunityCheck.id == check_id,
        OpportunityCheck.user_id == user_id,
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Opportunity check not found")
    return check


# ─── POST /check ──────────────────────────────────────────────────────────────

@router.post("/check", response_model=OpportunityCheckResponse, status_code=status.HTTP_201_CREATED)
async def check_opportunity(
    input_type: str = Form(...),
    text: str = Form(default=None),
    url: str = Form(default=None),
    file: UploadFile = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main endpoint: accepts a job opportunity via text, URL, image, or PDF,
    extracts structured data, verifies it, compares with student profile,
    and saves the result.
    """
    # Validate input_type
    try:
        itype = InputTypeEnum(input_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input_type. Must be one of: {[e.value for e in InputTypeEnum]}",
        )

    ocr_text = None
    file_path = None
    doc_record = None
    error_msg = None

    # ── Route to extractor ────────────────────────────────────────────────
    if itype == InputTypeEnum.text:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="text is required for input_type=text")
        extracted = extract_from_text(text)
        raw_input = text[:5000]

    elif itype == InputTypeEnum.url:
        if not url or not url.strip():
            raise HTTPException(status_code=400, detail="url is required for input_type=url")
        error_msg, extracted = await extract_from_url(url)
        raw_input = url

    elif itype in (InputTypeEnum.image, InputTypeEnum.screenshot):
        if not file:
            raise HTTPException(status_code=400, detail="file is required for image/screenshot input")
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images are supported")
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds 10 MB limit")

        # Save file
        save_dir = _upload_dir(current_user.id)
        safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'image.jpg')}"
        file_path = os.path.join(save_dir, safe_name)
        with open(file_path, "wb") as f_out:
            f_out.write(file_bytes)

        ocr_text, extracted = extract_from_image(file_bytes, file.content_type)
        raw_input = None

        doc_record = OpportunityDocument(
            filename=file.filename or safe_name,
            file_path=file_path,
            file_type=file.content_type,
            file_size=len(file_bytes),
            ocr_text=ocr_text[:5000] if ocr_text else None,
        )

    elif itype == InputTypeEnum.pdf:
        if not file:
            raise HTTPException(status_code=400, detail="file is required for input_type=pdf")
        if file.content_type not in (ALLOWED_PDF_TYPE, "application/octet-stream"):
            # Be lenient — browsers sometimes send different content-types for PDFs
            ext = os.path.splitext(file.filename or "")[1].lower()
            if ext != ".pdf":
                raise HTTPException(status_code=400, detail="Only PDF files are supported for this input type")
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds 10 MB limit")

        # Save file
        save_dir = _upload_dir(current_user.id)
        safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'document.pdf')}"
        file_path = os.path.join(save_dir, safe_name)
        with open(file_path, "wb") as f_out:
            f_out.write(file_bytes)

        pdf_text, extracted = extract_from_pdf(file_bytes)
        raw_input = None

        doc_record = OpportunityDocument(
            filename=file.filename or safe_name,
            file_path=file_path,
            file_type=file.content_type,
            file_size=len(file_bytes),
            ocr_text=pdf_text[:5000] if pdf_text else None,
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported input type")

    # ── Verify ────────────────────────────────────────────────────────────
    verification = verify_opportunity(extracted, source_text=ocr_text)

    # ── Compare with student profile ──────────────────────────────────────
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    student_skills = []
    if profile:
        student_skills = (
            db.query(StudentSkill)
            .filter(StudentSkill.profile_id == profile.id)
            .all()
        )

    apply_rec = compare_opportunity_with_profile(extracted, profile, student_skills)

    # ── Persist ───────────────────────────────────────────────────────────
    check = OpportunityCheck(
        user_id=current_user.id,
        input_type=itype,
        raw_input=raw_input,
        file_path=file_path,
        extracted_data=extracted.model_dump(),
        verification_status=verification.status,
        verification_score=verification.score,
        verification_details={
            "checks_performed": verification.checks_performed,
            "warning_signs": verification.warning_signs,
            "positive_signals": verification.positive_signals,
            "explanation": verification.explanation,
            "disclaimer": verification.disclaimer,
        },
        apply_recommendation=apply_rec.recommendation,
        apply_reasoning=apply_rec.reasoning,
    )
    # Add apply details into verification_details for convenience
    check.verification_details["apply_details"] = {
        "matched_skills": apply_rec.matched_skills,
        "missing_skills": apply_rec.missing_skills,
        "upskill_suggestions": apply_rec.upskill_suggestions,
    }

    db.add(check)
    db.flush()

    if doc_record:
        doc_record.opportunity_check_id = check.id
        db.add(doc_record)

    db.commit()
    db.refresh(check)
    return check


# ─── GET /history ─────────────────────────────────────────────────────────────

@router.get("/history", response_model=List[OpportunityCheckListItem])
def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all past opportunity checks for the current user, newest first."""
    return (
        db.query(OpportunityCheck)
        .filter(OpportunityCheck.user_id == current_user.id)
        .order_by(OpportunityCheck.created_at.desc())
        .all()
    )


# ─── GET /{check_id} ──────────────────────────────────────────────────────────

@router.get("/{check_id}", response_model=OpportunityCheckResponse)
def get_check(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific opportunity check with full detail."""
    return _get_check_or_404(check_id, current_user.id, db)


# ─── DELETE /{check_id} ───────────────────────────────────────────────────────

@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_check(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an opportunity check and all associated files."""
    check = _get_check_or_404(check_id, current_user.id, db)

    # Remove uploaded files
    for doc in check.documents:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except OSError:
                pass
    if check.file_path and os.path.exists(check.file_path):
        try:
            os.remove(check.file_path)
        except OSError:
            pass

    db.delete(check)
    db.commit()
