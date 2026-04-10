# backend/app/schemas/notification.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    type: str
    title: str
    message: str
    is_read: bool
    related_opportunity_id: Optional[UUID] = None
    related_application_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkRead(BaseModel):
    notification_ids: list[UUID]