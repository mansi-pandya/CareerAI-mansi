from datetime import datetime
import enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Text, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import JSON as GenericJSON
from sqlalchemy.orm import relationship

from app.database.database import Base


class InputTypeEnum(str, enum.Enum):
    screenshot = "screenshot"
    image = "image"
    pdf = "pdf"
    url = "url"
    text = "text"


class VerificationStatusEnum(str, enum.Enum):
    genuine = "genuine"
    could_not_verify = "could_not_verify"
    warning_signs = "warning_signs"


class ApplyRecommendationEnum(str, enum.Enum):
    apply_now = "apply_now"
    apply_upskill = "apply_upskill"
    consider_after_upskill = "consider_after_upskill"
    dont_prioritize = "dont_prioritize"


class OpportunityCheck(Base):
    __tablename__ = "opportunity_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    input_type = Column(SAEnum(InputTypeEnum), nullable=False)
    raw_input = Column(Text, nullable=True)          # pasted text or URL
    file_path = Column(String(500), nullable=True)   # saved file path (never returned as content)

    # Extracted structured data
    extracted_data = Column(GenericJSON, nullable=True)

    # Verification
    verification_status = Column(SAEnum(VerificationStatusEnum), nullable=True)
    verification_score = Column(Float, nullable=True)
    verification_details = Column(GenericJSON, nullable=True)

    # Apply recommendation
    apply_recommendation = Column(SAEnum(ApplyRecommendationEnum), nullable=True)
    apply_reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    documents = relationship(
        "OpportunityDocument",
        back_populates="opportunity_check",
        cascade="all, delete-orphan",
    )


class OpportunityDocument(Base):
    __tablename__ = "opportunity_documents"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_check_id = Column(Integer, ForeignKey("opportunity_checks.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)   # never returned as content
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)         # bytes
    ocr_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    opportunity_check = relationship("OpportunityCheck", back_populates="documents")
