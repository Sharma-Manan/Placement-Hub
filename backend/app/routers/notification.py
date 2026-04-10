# backend/app/routers/notification.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.notification import NotificationOut, NotificationMarkRead
from app.models.notification import Notification

notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])


# --------------------------------------------------
# GET /notifications → Get all notifications for current user
# --------------------------------------------------
@notification_router.get(
    "/",
    response_model=List[NotificationOut]
)
def get_my_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()

    return notifications


# --------------------------------------------------
# GET /notifications/unread-count → Get unread count
# --------------------------------------------------
@notification_router.get(
    "/unread-count",
    response_model=dict
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}


# --------------------------------------------------
# PATCH /notifications/read → Mark specific notifications as read
# --------------------------------------------------
@notification_router.patch(
    "/read",
    response_model=dict
)
def mark_notifications_read(
    payload: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.id.in_(payload.notification_ids),
        Notification.user_id == current_user.id  # security: own notifications only
    ).update(
        {"is_read": True},
        synchronize_session=False
    )

    db.commit()

    return {"message": "Notifications marked as read"}


# --------------------------------------------------
# PATCH /notifications/read-all → Mark ALL notifications as read
# --------------------------------------------------
@notification_router.patch(
    "/read-all",
    response_model=dict
)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update(
        {"is_read": True},
        synchronize_session=False
    )

    db.commit()

    return {"message": "All notifications marked as read"}


# --------------------------------------------------
# DELETE /notifications/{id} → Delete a single notification
# --------------------------------------------------
@notification_router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id  # security: own notifications only
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return None


# --------------------------------------------------
# DELETE /notifications → Clear all notifications
# --------------------------------------------------
@notification_router.delete(
    "/",
    response_model=dict
)
def clear_all_notifications(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "All notifications cleared"}