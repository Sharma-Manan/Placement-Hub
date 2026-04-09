from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class EligibilityRulesBase(BaseModel):
    # all optional — None means no restriction
    min_cgpa:        Optional[float]     = None
    max_backlogs:    Optional[int]       = None
    allowed_depts:   Optional[list[str]] = None
    allowed_batches: Optional[list[int]] = None
    allowed_branches: Optional[list[str]] = None
    no_prior_offer:  bool                = False  # default False, not None

    @field_validator("min_cgpa")
    @classmethod
    def cgpa_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 10.0):
            raise ValueError("min_cgpa must be between 0 and 10")
        return v

    @field_validator("max_backlogs")
    @classmethod
    def backlogs_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("max_backlogs cannot be negative")
        return v


class EligibilityRulesCreate(EligibilityRulesBase):
    # opportunity_id injected from URL, same pattern as company_id
    pass


class EligibilityRulesUpdate(BaseModel):
    min_cgpa:        Optional[float]     = None
    max_backlogs:    Optional[int]       = None
    allowed_depts:   Optional[list[str]] = None
    allowed_batches: Optional[list[int]] = None
    no_prior_offer:  Optional[bool]      = None


class EligibilityRulesOut(EligibilityRulesBase):
    id:             UUID
    opportunity_id: UUID

    model_config = ConfigDict(from_attributes=True)