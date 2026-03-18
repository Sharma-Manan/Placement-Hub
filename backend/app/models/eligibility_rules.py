from sqlalchemy import Column, Float, Integer, Boolean, ForeignKey, ARRAY, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class EligibilityRules(Base):
    __tablename__ = "eligibility_rules"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, unique=True)

    min_cgpa        = Column(Float, nullable=True)
    max_backlogs    = Column(Integer, nullable=True)
    allowed_depts   = Column(ARRAY(Text), nullable=True)
    allowed_batches = Column(ARRAY(Integer), nullable=True)
    no_prior_offer  = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  