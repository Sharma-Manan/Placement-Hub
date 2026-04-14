from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MentionedStudent(BaseModel):
    student_id: UUID
    student_name: str
    roll_no: Optional[str] = None


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    announcement_type: str = Field(
        default="general",
        description="One of: general, placement, deadline_extension, test_reminder, interview_reminder, custom"
    )
    related_opportunity_id: Optional[UUID] = None
    # List of student UUIDs to @mention
    mentioned_student_ids: Optional[List[UUID]] = None
    is_pinned: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Placement Update 🎉",
                "message": "@student:<uuid> has been placed at Google as SDE with 18 LPA!",
                "announcement_type": "placement",
                "mentioned_student_ids": ["uuid-of-student"],
                "is_pinned": True
            }
        }


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    is_pinned: Optional[bool] = None


class AnnouncementOut(BaseModel):
    id: UUID
    title: str
    message: str
    display_message: Optional[str] = None
    announcement_type: str
    related_opportunity_id: Optional[UUID] = None
    mentioned_students: Optional[List[MentionedStudent]] = None
    is_pinned: bool
    coordinator_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True