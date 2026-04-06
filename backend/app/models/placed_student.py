from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class PlacedStudent(Base):
    __tablename__ = "placed_students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    opportunity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
        nullable=True,
    )
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=True,
        unique=True,                  # one placed record per application
    )

    company_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    ctc_lpa = Column(Float, nullable=True)

    placed_at = Column(DateTime(timezone=True), server_default=func.now())