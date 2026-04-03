# app/models/application.py

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import text

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(
    UUID(as_uuid=True),
    primary_key=True,
    index=True,
    server_default=text("gen_random_uuid()")   
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    opportunity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="applied"
    )

    # 🔥 Student Snapshot (denormalized data)
    student_name = Column(String, nullable=False)
    student_email = Column(String, nullable=False)
    student_cgpa = Column(String, nullable=True)
    student_department = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("student_id", "opportunity_id", name="uq_student_opportunity"),
    )