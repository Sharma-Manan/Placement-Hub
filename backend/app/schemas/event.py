from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class EventCreate(BaseModel):
    opportunity_id: UUID
    event_type: str  # "test" or "interview"
    title: Optional[str] = None
    description: Optional[str] = None
    event_datetime: datetime
    duration_minutes: int
    location: Optional[str] = None

    student_ids: Optional[List[UUID]] = None  # manual assignment


class EventResponse(BaseModel):
    id: UUID
    opportunity_id: UUID
    event_type: str
    title: Optional[str]
    description: Optional[str]
    event_datetime: datetime
    duration_minutes: int
    location: Optional[str]

    class Config:
        from_attributes = True