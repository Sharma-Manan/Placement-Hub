from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

from enum import Enum

class BranchEnum(str, Enum):
    AE = "AE"
    CE = "CE"
    CSE = "CSE"
    EE = "EE"
    IT = "IT"
    ME = "ME"
    MT = "MT"

    ICT = "ICT"

    BBA = "BBA"
    BBA_HONS = "BBA (Hons)"
    BCOM_HONS = "B.Com"
    MBA = "MBA"



class StudentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    roll_no: str
    department_id: str
    branch: BranchEnum
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


class StudentProfileOut(BaseModel):
    first_name: str
    last_name: str
    roll_no: str
    department_id: str
    branch : BranchEnum
    graduation_year: int
    cgpa: float
    active_backlogs: int
    total_backlogs: int
    tenth_percentage: float
    twelfth_percentage: float
    resume_url: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    placement_status: Optional[str]
    is_profile_complete: bool
    profile_photo_url: Optional[str]

    class Config:
        from_attributes = True


# AI Data Extraction Schemas
class GitHubData(BaseModel):
    languages: list[str] = []
    repo_count: int = 0
    top_repos: list[str] = []
    stars: int = 0
    followers: int = 0
    activity_level: str = ""


class StudentAIDataCreate(BaseModel):
    skills: list[str] = []
    projects: list[dict] = []
    experience: list[dict] = []
    education: list[dict] = []
    certifications: list[dict] = []
    github: GitHubData = GitHubData()


class StudentAIDataOut(BaseModel):
    id: str
    user_id: str
    skills: list[str]
    projects: list[dict]
    experience: list[dict]
    education: list[dict]
    certifications: list[dict]
    github: GitHubData
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True