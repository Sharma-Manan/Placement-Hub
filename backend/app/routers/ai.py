from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import require_student
from app.schemas.auth import CurrentUser
from app.models.student import Student
from app.services.ai_extraction_service import parse_resume_from_url

ai_router = APIRouter(prefix="/ai", tags=["AI"])

@ai_router.post("/extract-resume")
async def extract_resume(data: dict):
    resume_url = data.get("resume_url")
    return parse_resume_from_url(resume_url)

@ai_router.get("/my-data")
async def get_my_data(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student or not student.resume_url:
        raise HTTPException(status_code=404, detail="No resume found")
    
    result = parse_resume_from_url(student.resume_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result