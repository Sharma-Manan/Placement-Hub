from pydantic import BaseModel, ConfigDict, field_validator, computed_field, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum
from app.schemas.eligibility_rules import EligibilityRulesOut
from fastapi import Form

class OpportunityStatus(str, Enum):
    draft  = "draft"
    active = "active"
    closed = "closed"


class OpportunityBase(BaseModel):
    title:                str
    description:          Optional[str]   = None
    location:             Optional[str]   = None
    additional_criteria: Optional[str] = None
    ctc_lpa:              float
    application_deadline: datetime
    # branch: Optional[list[str]] = None
    jd_url: Optional[str] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None

    @field_validator("ctc_lpa")
    @classmethod
    def ctc_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("ctc_lpa must be positive")
        return v

#changed
class OpportunityCreate(OpportunityBase):
    company_name: str
    @classmethod
    def as_form(
        cls,
        company_name: str = Form(...),
        title: str = Form(...),
        description: str = Form(None),
        location: str = Form(None),
        ctc_lpa: float = Form(...),
        application_deadline: datetime = Form(...),
        company_url: str = Form(None),
        company_logo: str = Form(None),
    ):
        return cls(
            company_name=company_name,
            title=title,
            description=description,
            location=location,
            ctc_lpa=ctc_lpa,
            application_deadline=application_deadline,
            company_url=company_url,
            company_logo=company_logo,
        )


class OpportunityUpdate(BaseModel):
    title:                Optional[str]               = None
    description:          Optional[str]               = None
    location:             Optional[str]               = None
    ctc_lpa:              Optional[float]             = None
    application_deadline: Optional[datetime]          = None
    status:               Optional[OpportunityStatus] = None

    @field_validator("ctc_lpa")
    @classmethod
    def ctc_must_be_positive(cls, v: float) -> float:
        if v is not None and v <= 0:
            raise ValueError("ctc_lpa must be positive")
        return v


class OpportunityOut(OpportunityBase):
    id:         UUID
    company_id: UUID          # present in output, injected in route not body
    company_name: str
    status:     OpportunityStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def is_accepting_applications(self) -> bool:
        now      = datetime.now(timezone.utc)
        deadline = self.application_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return self.status == OpportunityStatus.active and deadline > now




class OpportunityOutDetail(OpportunityOut):
    """
    GET /opportunities/{id}
    Includes eligibility so frontend can show
    "Requires 7.5 CGPA · No backlogs · CS/IT only"
    """
    eligibility: Optional[EligibilityRulesOut] = None


class OpportunityOutStudent(OpportunityOut):
    """
    GET /opportunities/eligible  (student dashboard)
    Pre-computed eligibility so frontend just reads booleans
    """
    is_eligible: bool = Field(
        ..., 
        description="Whether the student meets eligibility criteria"
    )
    has_applied: bool = Field(
        ..., 
        description="Whether the student has already applied to this opportunity"
    )
    ineligible_reason: Optional[str] = Field(
        None, 
        description="Reason why student is not eligible (if applicable)"
    )