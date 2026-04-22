from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class StudentAIData(Base):
    __tablename__ = "student_ai_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Extracted AI data stored as JSON
    skills = Column(JSON, default=[])
    projects = Column(JSON, default=[])
    experience = Column(JSON, default=[])
    education = Column(JSON, default=[])
    certifications = Column(JSON, default=[])
    github = Column(JSON, default={
        "languages": [],
        "repo_count": 0,
        "top_repos": [],
        "stars": 0,
        "followers": 0,
        "activity_level": ""
    })
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
