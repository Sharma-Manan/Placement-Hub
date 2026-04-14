from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who sent it
    coordinator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Type: "general" | "placement" | "deadline_extension" | "test_reminder" | "interview_reminder" | "custom"
    announcement_type = Column(String(50), nullable=False, default="general")

    # Optional: tag a specific opportunity
    related_opportunity_id = Column(UUID(as_uuid=True), nullable=True)

    # Mentions: list of student user_ids mentioned with @
    # stored as array of UUIDs
    mentioned_student_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Parsed display text with @mentions resolved (stored for quick rendering)
    # e.g. "@Rahul Sharma is placed at Google!"
    # The raw message has @student:<uuid> tokens, display_message has names
    display_message = Column(Text, nullable=True)

    is_pinned = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())