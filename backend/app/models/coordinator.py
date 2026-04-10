from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Coordinator(Base):
    __tablename__ = "coordinators"

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

    # ✅ CHANGED: first_name and last_name now get it from User
    # So we don't need to duplicate them here
    # But if you want to keep them, make them nullable
    first_name = Column(String, nullable=True)  # ✅ CHANGED
    last_name = Column(String, nullable=True)  # ✅ CHANGED
    profile_photo_url = Column(String, nullable=True) 
    profile_photo_public_id = Column(String, nullable=True)

    is_primary = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )