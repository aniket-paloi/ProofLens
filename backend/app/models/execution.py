import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class ProcessingRun(Base):
    __tablename__ = "processing_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), default="QUEUED", index=True)  # QUEUED, RUNNING, COMPLETED, FAILED, PARTIAL
    snapshot_hash = Column(String(64), nullable=False)        # SHA-256 of documents and config
    config_version = Column(String(32), default="1.0.0")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    case = relationship("Case", back_populates="runs")
    fields = relationship("Field", back_populates="run", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="run", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="run", cascade="all, delete-orphan")
    check_executions = relationship("CheckExecution", back_populates="run", cascade="all, delete-orphan")
    observations = relationship("VisualObservation", back_populates="run", cascade="all, delete-orphan")
    tool_executions = relationship("ToolExecution", back_populates="run", cascade="all, delete-orphan")

class CheckDefinition(Base):
    __tablename__ = "check_definitions"

    id = Column(String(64), primary_key=True)  # e.g., CHK_SALARY_RECON, CHK_TEXT_LAYER_SYNC
    category = Column(String(64), nullable=False) # FINANCIAL, VISUAL, STRUCTURAL, CROSS_DOCUMENT
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    is_mandatory = Column(Integer, default=1)

class CheckExecution(Base):
    __tablename__ = "check_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    check_id = Column(String(64), ForeignKey("check_definitions.id"), nullable=False)
    
    lifecycle_state = Column(String(32), default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED
    applicability = Column(String(32), default="APPLICABLE")   # APPLICABLE, NOT_APPLICABLE, UNSUPPORTED
    outcome = Column(String(32), default="UNABLE_TO_ASSESS")    # CONSISTENT, DISCREPANCY, POSSIBLE_EXPLANATION, INSUFFICIENT_EVIDENCE, UNABLE_TO_ASSESS
    
    assumptions = Column(JSON, default=list)
    parameters_used = Column(JSON, default=dict)
    inspected_evidence_ids = Column(JSON, default=list)
    scoped_limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    run = relationship("ProcessingRun", back_populates="check_executions")

class VisualObservation(Base):
    __tablename__ = "visual_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    
    detector_name = Column(String(64), nullable=False)  # font_baseline, sharpness_variance, mobilenet_small
    detector_version = Column(String(32), default="1.0.0")
    measured_property = Column(String(128), nullable=False)  # e.g., sharpness_ratio, font_mismatch_score
    measured_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    
    bbox_normalized = Column(JSON, nullable=False)
    comparison_region_bbox = Column(JSON, nullable=True)
    crop_path = Column(String(512), nullable=True)
    evidence_strength = Column(String(32), default="LOW")  # LOW, MEDIUM, HIGH
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    run = relationship("ProcessingRun", back_populates="observations")

class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("processing_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(64), nullable=False)
    arguments = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    run = relationship("ProcessingRun", back_populates="tool_executions")

