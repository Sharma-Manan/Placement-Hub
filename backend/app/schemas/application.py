# app/schemas/application.py

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from typing import Literal
from pydantic import BaseModel

# -----------------------------
# 1. Basic Application Response
# -----------------------------
class ApplicationOut(BaseModel):
    id: UUID
    student_id: UUID
    opportunity_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# 2. Status Update (Coordinator)
# -----------------------------
class ApplicationStatusUpdate(BaseModel):
    status: Literal["applied", "shortlisted", "rejected", "selected"]


# -----------------------------
# 3. Student View (Nested Data)
# -----------------------------
class ApplicationOutStudent(BaseModel):
    id: UUID
    status: str
    created_at: datetime

    # Opportunity info
    opportunity_id: UUID
    opportunity_title: str
    company_name: str
    application_deadline: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)