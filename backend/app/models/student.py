from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    roll_no = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    department_id = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)

    cgpa = Column(Numeric(3, 2))
    active_backlogs = Column(Integer, default=0)
    total_backlogs = Column(Integer, default=0)

    tenth_percentage = Column(Numeric(5, 2))
    twelfth_percentage = Column(Numeric(5, 2))

    resume_url = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    portfolio_url = Column(String)

    placement_status = Column(String, default="unplaced")
    is_profile_complete = Column(Boolean, default=False)

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
        CheckConstraint(
            "active_backlogs <= total_backlogs",
            name="chk_backlogs_consistency",
        ),
        CheckConstraint(
            "placement_status IN ('unplaced', 'offer_received', 'placed')",
            name="chk_placement_status",
        ),
    )
