from pydantic import BaseModel, HttpUrl
from typing import Literal

class StudentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    # phone_number: str
    roll_no: str
    department_id: str
    # branch: str
    graduation_year: int
    cgpa: float  
    active_backlogs: int
    total_backlogs: int
    tenth_percentage: float
    twelfth_percentage: float
    resume_url: str
    linkedin_url: str
    github_url: str
    portfolio_url: str
    placement_status: Literal["placed", "unplaced", "offer_received"]
    is_profile_complete: bool = False

class CoordinatorProfileCreate(BaseModel):
    is_primary: bool = True

class CompanyProfileCreate(BaseModel):
    first_name: str
    last_name: str
    name: str
    website_url: HttpUrl
    logo_url: HttpUrl
    industry: str
    description: str

