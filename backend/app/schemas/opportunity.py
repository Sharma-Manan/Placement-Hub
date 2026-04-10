from pydantic import BaseModel, ConfigDict, field_validator, computed_field, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum
from app.schemas.eligibility_rules import EligibilityRulesOut


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
    is_eligible:       bool
    has_applied:       bool
    ineligible_reason: Optional[str] = None  # "Requires 8.0 CGPA (you have 7.2)"




class OpportunityOutStudent(BaseModel):
    """
    Opportunity response for students with eligibility and application status
    """
    id: UUID
    title: str
    company_name: str
    description: Optional[str] = None
    location: Optional[str] = None
    ctc_lpa: Optional[float] = None
    application_deadline: Optional[datetime] = None
    eligibility: Optional[Dict[str, Any]] = None
    is_accepting_applications: bool = True
    created_at: datetime
    updated_at: datetime
    
    # Student-specific fields
    has_applied: bool = Field(
        ..., 
        description="Whether the student has already applied to this opportunity"
    )
    is_eligible: bool = Field(
        ..., 
        description="Whether the student meets eligibility criteria"
    )
    ineligible_reason: Optional[str] = Field(
        None, 
        description="Reason why student is not eligible (if applicable)"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Software Engineer",
                "company_name": "Google",
                "description": "Full-stack development role",
                "location": "Bangalore",
                "ctc_lpa": 15.0,
                "application_deadline": "2025-05-01T23:59:59",
                "eligibility": {
                    "min_cgpa": 7.5,
                    "max_backlogs": 0,
                    "allowed_depts": ["CSE", "IT"],
                    "allowed_batches": [2025]
                },
                "is_accepting_applications": True,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "has_applied": False,
                "is_eligible": True,
                "ineligible_reason": None
            }
        }