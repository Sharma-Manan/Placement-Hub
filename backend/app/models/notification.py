from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    # Student - Opportunity
    NEW_OPPORTUNITY = "new_opportunity"
    ELIGIBLE_OPPORTUNITY = "eligible_opportunity"
    DEADLINE_REMINDER = "deadline_reminder"

    # Student - Application
    APPLICATION_SUBMITTED = "application_submitted"
    STATUS_SHORTLISTED = "status_shortlisted"
    STATUS_REJECTED = "status_rejected"
    STATUS_TEST_SCHEDULED = "status_test_scheduled"
    STATUS_INTERVIEW_SCHEDULED = "status_interview_scheduled"
    STATUS_OFFERED = "status_offered"

    # Student - Offer
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OTHER_OFFERS_REJECTED = "other_offers_rejected"

    # Student - Schedule
    TEST_SCHEDULED = "test_scheduled"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    SCHEDULE_REMINDER = "schedule_reminder"
    SCHEDULE_CONFLICT = "schedule_conflict"

    # Coordinator - Applications
    NEW_APPLICATION = "new_application"
    HIGH_APPLICATIONS = "high_applications"
    LOW_APPLICATIONS = "low_applications"

    # Coordinator - Alerts
    COORDINATOR_CONFLICT_ALERT = "coordinator_conflict_alert"
    DEADLINE_APPROACHING = "deadline_approaching"

    # Coordinator - Placement
    STUDENT_OFFER_ACCEPTED = "student_offer_accepted"
    WALL_OF_FAME_ADDED = "wall_of_fame_added"

    # Announcements
    ANNOUNCEMENT = "announcement"
    ANNOUNCEMENT_MENTIONED = "announcement_mentioned"


class NotificationRole(str, enum.Enum):
    student = "student"
    coordinator = "coordinator"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(String, nullable=False)  # "student" or "coordinator"

    type = Column(String, nullable=False)  # NotificationType value

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False, nullable=False)

    # Optional reference to related entity
    related_opportunity_id = Column(UUID(as_uuid=True), nullable=True)
    related_application_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())