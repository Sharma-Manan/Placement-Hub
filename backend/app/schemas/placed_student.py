from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class PlacedStudentListOut(BaseModel):
    id: UUID
    user_id: UUID
    roll_no: str
    first_name: str
    last_name: str
    department_id: str
    graduation_year: int
    cgpa: Optional[float]
    placement_status: str

    class Config:
        from_attributes = True