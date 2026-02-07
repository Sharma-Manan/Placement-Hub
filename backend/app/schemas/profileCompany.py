from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class CompanyBase(BaseModel):
    name: str
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

