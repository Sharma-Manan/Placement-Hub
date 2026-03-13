from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class OpportunityBase(BaseModel):
    company_id: UUID
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    application_deadline: datetime


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    application_deadline: Optional[datetime] = None


class OpportunityOut(OpportunityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)