from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.student import Student
from app.models.student_ai_data import StudentAIData
from app.schemas.auth import CurrentUser
from app.core.dependencies import require_student, require_coordinator
from app.services.ai_extraction_service import extract_text_from_pdf, extract_resume_data

ai_extraction_router = APIRouter(prefix="/ai", tags=["AI Extraction"])


@ai_extraction_router.post("/extract-resume")
async def extract_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
    """
    Upload a resume PDF → AI extracts structured data → saves to student_ai_data.
    If data already exists for this student, it gets replaced (upsert).
    """
    # 1. Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")

    # 2. Get student record
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found. Create your profile first.")

    # 3. Extract text from PDF
    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {str(e)}")

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract enough text from the PDF. Make sure it's not a scanned image."
        )

    # 4. Send to AI for extraction
    try:
        extracted = extract_resume_data(raw_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # 5. Upsert into student_ai_data
    existing = db.query(StudentAIData).filter_by(student_id=student.id).first()

    if existing:
        existing.skills = extracted["skills"]
        existing.education = extracted["education"]
        existing.projects = extracted["projects"]
        existing.experience = extracted["experience"]
        existing.certifications = extracted["certifications"]
        existing.summary = extracted["summary"]
        existing.raw_text = raw_text
        existing.extracted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        ai_data = existing
    else:
        ai_data = StudentAIData(
            student_id=student.id,
            skills=extracted["skills"],
            education=extracted["education"],
            projects=extracted["projects"],
            experience=extracted["experience"],
            certifications=extracted["certifications"],
            summary=extracted["summary"],
            raw_text=raw_text,
        )
        db.add(ai_data)
        db.commit()
        db.refresh(ai_data)

    return {
        "message": "Resume extracted successfully",
        "data": {
            "id": str(ai_data.id),
            "student_id": str(ai_data.student_id),
            "skills": ai_data.skills,
            "education": ai_data.education,
            "projects": ai_data.projects,
            "experience": ai_data.experience,
            "certifications": ai_data.certifications,
            "summary": ai_data.summary,
            "extracted_at": ai_data.extracted_at,
        },
    }


@ai_extraction_router.get("/my-data")
def get_my_ai_data(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
    """Get the current student's AI-extracted resume data."""
    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    ai_data = db.query(StudentAIData).filter_by(student_id=student.id).first()
    if not ai_data:
        raise HTTPException(status_code=404, detail="No AI-extracted data found. Upload your resume first.")

    return {
        "id": str(ai_data.id),
        "student_id": str(ai_data.student_id),
        "skills": ai_data.skills,
        "education": ai_data.education,
        "projects": ai_data.projects,
        "experience": ai_data.experience,
        "certifications": ai_data.certifications,
        "summary": ai_data.summary,
        "extracted_at": ai_data.extracted_at,
    }


@ai_extraction_router.get("/student/{student_id}")
def get_student_ai_data(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    """Coordinator endpoint: view any student's AI-extracted data."""
    ai_data = db.query(StudentAIData).filter_by(student_id=student_id).first()
    if not ai_data:
        raise HTTPException(status_code=404, detail="No AI-extracted data found for this student")

    return {
        "id": str(ai_data.id),
        "student_id": str(ai_data.student_id),
        "skills": ai_data.skills,
        "education": ai_data.education,
        "projects": ai_data.projects,
        "experience": ai_data.experience,
        "certifications": ai_data.certifications,
        "summary": ai_data.summary,
        "extracted_at": ai_data.extracted_at,
    }
