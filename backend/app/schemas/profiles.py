from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

class StudentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    roll_no: str
    department_id: str
    graduation_year: int
    cgpa: float  
    active_backlogs: int
    total_backlogs: int
    tenth_percentage: float
    twelfth_percentage: float
    resume_url: str
    linkedin_url: HttpUrl
    github_url: HttpUrl
    portfolio_url: HttpUrl
    profile_photo_url: Optional[str] = None   
    placement_status: Literal["placed", "unplaced", "offer_received"] = "unplaced"
    is_profile_complete: bool = False

class CoordinatorProfileCreate(BaseModel):
    first_name: str
    last_name: str
    profile_photo_url: Optional[str] = None   
    is_primary: bool = True

class CompanyProfileCreate(BaseModel):
    name: str
    website_url: HttpUrl
    logo_url: HttpUrl
    industry: str
    description: str

