# # app/models/wall_of_fame.py

# from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.sql import func
# import uuid
# from app.db.base import Base


# class WallOfFame(Base):
#     __tablename__ = "wall_of_fame"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     placed_student_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("placed_students.id", ondelete="CASCADE"),
#         nullable=False,
#         unique=True,                  # one wall entry per placed student
#     )

#     greeting = Column(String(300), nullable=False)
#     is_featured = Column(Boolean, default=False)
#     display_order = Column(Integer, default=0)

#     added_by = Column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id"),
#         nullable=True,
#     )

#     created_at = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class WallOfFame(Base):
    __tablename__ = "wall_of_fame"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    placed_student_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("placed_students.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # Each student can only be in wall once
    )
    greeting = Column(String(500), nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)  # ← Add this
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())