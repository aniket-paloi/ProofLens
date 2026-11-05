import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Field(Base):
    __tablename__ = "fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    field_name = Column(String(128), nullable=False, index=True)  # e.g., gross_salary, net_salary, applicant_name
    raw_value = Column(String(512), nullable=False)
    normalized_value = Column(String(512), nullable=True)
    numeric_value = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(8), default="INR")
    period_start = Column(String(32), nullable=True)  # YYYY-MM-DD
    period_end = Column(String(32), nullable=True)    # YYYY-MM-DD
    
    # Normalized top-left coordinates [ymin, xmin, ymax, xmax] in [0, 1]
    bbox_normalized = Column(JSON, nullable=False)
    # Original coordinates and transform metadata
    bbox_original = Column(JSON, nullable=True)
    source_token_ids = Column(JSON, default=list)
    
    extractor_name = Column(String(64), nullable=False)  # pymupdf, paddleocr, llm_adapter
    extractor_version = Column(String(32), default="1.0.0")
    extraction_score = Column(Float, default=1.0)
    current_revision_num = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)

    page = relationship("Page", back_populates="fields")
    run = relationship("ProcessingRun", back_populates="fields")
    revisions = relationship("FieldRevision", back_populates="field", cascade="all, delete-orphan")

class FieldRevision(Base):
    __tablename__ = "field_revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    actor_id = Column(String(64), nullable=False)  # username / reviewer ID
    reason = Column(String(512), nullable=False)
    previous_value = Column(String(512), nullable=False)
    new_value = Column(String(512), nullable=False)
    new_numeric_value = Column(Numeric(14, 2), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    field = relationship("Field", back_populates="revisions")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_type = Column(String(64), nullable=False)  # SALARY_CLAIM, IDENTITY_CLAIM, BALANCE_CLAIM
    subject = Column(String(255), nullable=False)     # Applicant Name / ID
    basis = Column(String(64), nullable=False)       # GROSS_SALARY, NET_SALARY, BANK_CREDIT, DECLARED_ANNUAL
    amount = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(8), default="INR")
    period_start = Column(String(32), nullable=True)
    period_end = Column(String(32), nullable=True)
    status = Column(String(32), default="ASSERTED")  # ASSERTED, VERIFIED, CONTRADICTED, UNKNOWN
    supporting_field_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    run = relationship("ProcessingRun", back_populates="claims")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(String(32), nullable=False)
    narration = Column(String(512), nullable=False)
    transaction_type = Column(String(16), nullable=False)  # CREDIT, DEBIT
    amount = Column(Numeric(14, 2), nullable=False)
    running_balance = Column(Numeric(14, 2), nullable=True)
    is_salary_candidate = Column(Integer, default=0)       # 1: Yes, 0: No
    bbox_normalized = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

