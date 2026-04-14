from sqlalchemy import Column, Text, DateTime, ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timezone


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

    # ✅ FIXED TYPE (important)
    ctc_lpa     = Column(Float, nullable=False)

    status      = Column(String, nullable=False, default="draft")

    jd_url = Column(Text, nullable=True)
    company_url = Column(Text, nullable=True)
    company_logo = Column(Text, nullable=True)

    application_deadline = Column(DateTime(timezone=True), nullable=False)
    # optional denormalized field
    company_name = Column(String, nullable=True)

    additional_criteria = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())