from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class WallOfFameCreate(BaseModel):
    """Schema for creating wall of fame entry"""
    placed_student_id: UUID = Field(..., description="ID of the placed student")
    greeting: str = Field(..., min_length=1, max_length=500, description="Congratulatory message")
    is_featured: Optional[bool] = Field(False, description="Whether to feature this student")
    
    class Config:
        json_schema_extra = {
            "example": {
                "placed_student_id": "123e4567-e89b-12d3-a456-426614174000",
                "greeting": "Happy to join Google as SDE! Thanks to Indus placement cell.",
                "is_featured": True
            }
        }


class WallOfFameUpdate(BaseModel):
    """Schema for updating wall of fame entry"""
    greeting: Optional[str] = Field(None, min_length=1, max_length=500)
    is_featured: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "greeting": "Updated greeting message",
                "is_featured": True
            }
        }


class WallOfFameEnhanced(BaseModel):
    """Enhanced wall of fame response with complete student details"""
    # Wall entry details
    id: UUID
    greeting: str
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    
    # Student details
    student_id: UUID
    student_name: str
    student_photo_url: Optional[str] = None
    roll_no: str
    department_id: str
    graduation_year: int
    cgpa: float
    
    # Placement details
    company_name: Optional[str] = None
    ctc_lpa: Optional[float] = None
    placed_at: Optional[datetime] = None
    
    # Contact/Social
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "greeting": "Happy to join Google as SDE!",
                "is_featured": True,
                "created_at": "2025-01-15T10:00:00",
                "updated_at": "2025-01-15T10:00:00",
                "student_id": "456e7890-e89b-12d3-a456-426614174001",
                "student_name": "Rahul Sharma",
                "student_photo_url": "https://cloudinary.com/photo.jpg",
                "roll_no": "21CSE101",
                "department_id": "CSE",
                "graduation_year": 2025,
                "cgpa": 8.5,
                "company_name": "Google",
                "ctc_lpa": 15.0,
                "placed_at": "2025-01-10T00:00:00",
                "linkedin_url": "https://linkedin.com/in/rahul",
                "github_url": "https://github.com/rahul"
            }
        }