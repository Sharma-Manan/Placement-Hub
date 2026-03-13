from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from app.core.security import get_current_user
from app.models.user import User

upload_router = APIRouter(prefix="/upload", tags=["Upload"])

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@upload_router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate PDF only
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Validate file size (5MB max)
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")

    # Upload to Supabase Storage
    file_name = f"resumes/{current_user.id}_{file.filename}"
    
    try:
        supabase_admin.storage.from_("student-resumes").upload(
            file_name,
            file_bytes,
            {"content-type": "application/pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Get public URL
    url = supabase_admin.storage.from_("student-resumes").get_public_url(file_name)
    
    return {"resume_url": url}