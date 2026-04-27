from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    cgpa: Optional[str] = None


class ProjectItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = []


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class CertificationItem(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[str] = None


class StudentAIDataOut(BaseModel):
    id: str
    student_id: str
    skills: Optional[List[str]] = []
    education: Optional[List[EducationItem]] = []
    projects: Optional[List[ProjectItem]] = []
    experience: Optional[List[ExperienceItem]] = []
    certifications: Optional[List[CertificationItem]] = []
    summary: Optional[str] = None
    extracted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIExtractionResponse(BaseModel):
    message: str
    data: StudentAIDataOut
