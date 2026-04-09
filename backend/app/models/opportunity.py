from sqlalchemy import Column, Text, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy import Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    title       = Column(Text, nullable=False)
    description = Column(Text)
    location    = Column(Text)
    ctc_lpa     = Column(Text)  # was salary
    status      = Column(String, nullable=False, default="draft")  # was missing
    branch = Column(ARRAY(String), nullable=True)
    jd_url = Column(Text, nullable=True)           # uploaded file URL
    company_url = Column(Text, nullable=True)
    company_logo = Column(Text, nullable=True)

    application_deadline = Column(DateTime(timezone=True), nullable=False)

    company_name = Column(String, nullable=True)  # denormalized for fast access

    is_accepting_applications = Column(
        Boolean,
        nullable=False,
        default=True
    )

    additional_criteria = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())