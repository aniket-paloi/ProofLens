import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    observation_type = Column(String(64), nullable=False) # CONTEXTUAL_MISMATCH, VISUAL_ANOMALY, TEXT_LAYER_DESYNC, MISSING_COVERAGE
    severity = Column(String(16), default="MEDIUM")       # INFO, LOW, MEDIUM, HIGH, CRITICAL
    uncertainty = Column(String(16), default="MEDIUM")    # LOW, MEDIUM, HIGH
    summary = Column(Text, nullable=False)
    
    alternative_explanations = Column(JSON, default=list) # e.g. ["Split salary payment", "Delayed credit across month boundary"]
    next_recommended_checks = Column(JSON, default=list)  # e.g. ["Request complete statement for following month"]
    
    # Reviewer disposition (independent of detector output)
    reviewer_disposition = Column(String(32), default="UNREVIEWED") # UNREVIEWED, CONFIRMED, DISMISSED, FURTHER_VERIFICATION_NEEDED
    reviewer_notes = Column(Text, nullable=True)
    reviewer_actor_id = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("Case", back_populates="findings")
    run = relationship("ProcessingRun", back_populates="findings")
    evidence_links = relationship("EvidenceLink", back_populates="finding", cascade="all, delete-orphan")
    review_actions = relationship("ReviewAction", back_populates="finding", cascade="all, delete-orphan")

class EvidenceLink(Base):
    __tablename__ = "evidence_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(32), nullable=False) # FIELD, CLAIM, TRANSACTION, OBSERVATION, DOCUMENT, PAGE
    entity_id = Column(String(36), nullable=False)
    role = Column(String(32), default="SUPPORTING")  # PRIMARY, CONTRADICTING, CORROBORATING, COMPARISON_BASELINE
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    finding = relationship("Finding", back_populates="evidence_links")

class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(String(64), nullable=False)
    disposition = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    finding = relationship("Finding", back_populates="review_actions")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    action_type = Column(String(64), nullable=False) # CASE_CREATED, DOCUMENT_UPLOADED, RUN_STARTED, FIELD_REVISED, FINDING_REVIEWED, REPORT_GENERATED
    actor_id = Column(String(64), default="system")
    payload_json = Column(Text, nullable=False)      # Canonical JSON string
    previous_event_hash = Column(String(64), nullable=False)
    current_event_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("Case", back_populates="audit_events")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="REVIEWER")
    created_at = Column(DateTime, default=utc_now, nullable=False)

