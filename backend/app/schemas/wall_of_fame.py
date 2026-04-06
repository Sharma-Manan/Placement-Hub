# app/schemas/wall_of_fame.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class WallOfFameCreate(BaseModel):
    placed_student_id: UUID          # from search result
    greeting: str                    # max 300 chars, only text input

class WallOfFameUpdate(BaseModel):
    greeting: Optional[str] = None
    is_featured: Optional[bool] = None

class WallOfFameOut(BaseModel):
    id: UUID
    student_name: str                # auto-pulled via JOIN
    roll_no: str                     # auto-pulled via JOIN
    photo_url: Optional[str]         # auto-pulled via JOIN
    batch_year: int                  # auto-pulled via JOIN
    branch: str                      # auto-pulled via JOIN
    company_name: str                # auto-pulled from PlacedStudent
    role: str                        # auto-pulled from PlacedStudent
    ctc_lpa: Optional[float]         # auto-pulled from PlacedStudent
    greeting: str
    is_featured: bool
    placed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True