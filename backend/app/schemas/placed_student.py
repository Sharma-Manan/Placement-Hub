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

class PlacedStudentOut(BaseModel):
    placed_student_id: UUID
    student_name: str
    company_name: str
    role: str
    ctc_lpa: Optional[float]
    already_on_wall: bool

    class Config:
        orm_mode = True