from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, unique=True, nullable=True)

    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'coordinator', 'company')",
            name="chk_user_role"
        ),
    )
