import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reference_number = Column(String(64), unique=True, nullable=False, index=True)
    applicant_name = Column(String(255), nullable=False)
    status = Column(String(32), default="ACTIVE", index=True)  # ACTIVE, REVIEWED, ARCHIVED
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    runs = relationship("ProcessingRun", back_populates="case", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(64), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    original_path = Column(String(512), nullable=False)
    classified_type = Column(String(64), default="UNKNOWN")  # APPLICATION_FORM, SALARY_SLIP, BANK_STATEMENT, UNKNOWN
    classification_confidence = Column(Float, default=0.0)
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("Case", back_populates="documents")
    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)  # 1-indexed
    width_pts = Column(Float, nullable=False)
    height_pts = Column(Float, nullable=False)
    rotation_deg = Column(Integer, default=0)
    rendered_image_path = Column(String(512), nullable=True)
    has_native_text = Column(Integer, default=1)  # 1: Yes, 0: Scanned/Raster only
    created_at = Column(DateTime, default=utc_now, nullable=False)

    document = relationship("Document", back_populates="pages")
    fields = relationship("Field", back_populates="page")

    @property
    def rendered_image_url(self) -> str:
        return f"/api/documents/{self.document_id}/pages/{self.page_number}/image"

