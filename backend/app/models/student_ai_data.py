from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class StudentAIData(Base):
    __tablename__ = "student_ai_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # AI-extracted fields
    skills = Column(JSON, default=[])
    education = Column(JSON, default=[])
    projects = Column(JSON, default=[])
    experience = Column(JSON, default=[])
    certifications = Column(JSON, default=[])
    summary = Column(Text, nullable=True)

    # Raw text for re-processing
    raw_text = Column(Text, nullable=True)

    # Metadata
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
