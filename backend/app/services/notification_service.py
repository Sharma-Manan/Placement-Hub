# backend/app/services/notification_service.py

from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification
from app.models.user import User
from app.models.coordinator import Coordinator


# --------------------------------------------------
# Core: Create a single notification
# --------------------------------------------------
def create_notification(
    db: Session,
    user_id: UUID,
    role: str,
    type: str,
    title: str,
    message: str,
    related_opportunity_id: UUID = None,
    related_application_id: UUID = None,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        role=role,
        type=type,
        title=title,
        message=message,
        related_opportunity_id=related_opportunity_id,
        related_application_id=related_application_id,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# --------------------------------------------------
# Notify a specific student (by user_id)
# --------------------------------------------------
def notify_student(
    db: Session,
    user_id: UUID,
    type: str,
    title: str,
    message: str,
    related_opportunity_id: UUID = None,
    related_application_id: UUID = None,
):
    return create_notification(
        db=db,
        user_id=user_id,
        role="student",
        type=type,
        title=title,
        message=message,
        related_opportunity_id=related_opportunity_id,
        related_application_id=related_application_id,
    )


# --------------------------------------------------
# Notify all coordinators
# --------------------------------------------------
def notify_all_coordinators(
    db: Session,
    type: str,
    title: str,
    message: str,
    related_opportunity_id: UUID = None,
    related_application_id: UUID = None,
):
    # Get all coordinator user_ids
    coordinators = db.query(Coordinator).all()

    for coordinator in coordinators:
        create_notification(
            db=db,
            user_id=coordinator.user_id,
            role="coordinator",
            type=type,
            title=title,
            message=message,
            related_opportunity_id=related_opportunity_id,
            related_application_id=related_application_id,
        )


# --------------------------------------------------
# Notify multiple students at once (bulk)
# --------------------------------------------------
def notify_students_bulk(
    db: Session,
    user_ids: list[UUID],
    type: str,
    title: str,
    message: str,
    related_opportunity_id: UUID = None,
    related_application_id: UUID = None,
):
    notifications = [
        Notification(
            user_id=uid,
            role="student",
            type=type,
            title=title,
            message=message,
            related_opportunity_id=related_opportunity_id,
            related_application_id=related_application_id,
        )
        for uid in user_ids
    ]

    db.bulk_save_objects(notifications)
    db.commit()