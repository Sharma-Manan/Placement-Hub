# from sqlalchemy import (
#     Column,
#     String,
#     Integer,
#     Numeric,
#     Boolean,
#     DateTime,
#     ForeignKey,
#     CheckConstraint,
# )
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.sql import func
# import uuid

# from app.db.base import Base


# class Student(Base):
#     __tablename__ = "students"

#     id = Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#         index=True,
#     )

#     user_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         unique=True,
#         index=True,
#     )

#     roll_no = Column(String, nullable=False, unique=True)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)

#     department_id = Column(String, nullable=False)
#     graduation_year = Column(Integer, nullable=False)

#     cgpa = Column(Numeric(4, 2)) 
#     active_backlogs = Column(Integer, default=0)
#     total_backlogs = Column(Integer, default=0)

#     tenth_percentage = Column(Numeric(5, 2))
#     twelfth_percentage = Column(Numeric(5, 2))

#     resume_url = Column(String)
#     linkedin_url = Column(String)
#     github_url = Column(String)
#     portfolio_url = Column(String)
#     profile_photo_url = Column(String, nullable=True) 

#     placement_status = Column(String, default="unplaced")
#     has_accepted_offer = Column(Boolean, default=False)
#     is_profile_complete = Column(Boolean, default=False)

#     created_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#     )

#     updated_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#     )

#     __table_args__ = (
#         CheckConstraint(
#             "active_backlogs <= total_backlogs",
#             name="chk_backlogs_consistency",
#         ),
#         CheckConstraint(
#             "placement_status IN ('unplaced', 'offer_received', 'placed')",
#             name="chk_placement_status",
#         ),
#     )

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Student(Base):
    __tablename__ = "students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Basic info
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    roll_no = Column(String, unique=True, nullable=False)
    department_id = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)
    branch = Column(String, nullable=True)

    
    # Academic
    cgpa = Column(Float, nullable=False)
    active_backlogs = Column(Integer, default=0)
    total_backlogs = Column(Integer, default=0)
    tenth_percentage = Column(Float, nullable=False)
    twelfth_percentage = Column(Float, nullable=False)
    
    # Documents & Links
    resume_url = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    portfolio_url = Column(String)
    profile_photo_url = Column(String)
    
    # Placement status
    placement_status = Column(String, default="unplaced")  # unplaced, placed, opted_out
    is_profile_complete = Column(Boolean, default=False)
    
    # ✅ ADD THESE NEW FIELDS for placement tracking
    placed_company_name = Column(String, nullable=True)
    placed_ctc_lpa = Column(Float, nullable=True)
    placed_at = Column(DateTime(timezone=True), nullable=True)
    offer_letter_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())