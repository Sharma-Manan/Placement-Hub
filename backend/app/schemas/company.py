from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    website_url: Optional[HttpUrl] = None   # use HttpUrl, not str — free validation
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass
    # NOTE: created_by is NOT here — inject it from JWT in the route:
    #   company_in.created_by = current_user.id


class CompanyUpdate(BaseModel):           # do NOT extend CompanyBase
    name: Optional[str] = None            # every field optional for PATCH
    website_url: Optional[HttpUrl] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None


class CompanyOut(CompanyBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class CompanyOutList(BaseModel):          # for paginated list responses
    items: list[CompanyOut]
    total: int
    page: int
    page_size: int