import os
import uuid
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.core.config import SUPABASE_KEY,SUPABASE_URL,JD_BUCKETNAME





# =========================================================
# 🚀 INIT CLIENT
# =========================================================
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are not set properly")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================================================
# 📤 FILE UPLOAD FUNCTION
# =========================================================
def upload_to_supabase(file: UploadFile) -> str:
    """
    Upload a PDF file to Supabase Storage and return public URL
    """

    # ✅ Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # ✅ Generate unique filename
    file_ext = file.filename.split(".")[-1] if file.filename else "pdf"
    file_name = f"{uuid.uuid4()}.{file_ext}"

    try:
        # ✅ Read file content
        file_bytes = file.file.read()

        # ✅ Optional: File size limit (5MB)
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 5MB)"
            )

        # ✅ Upload to Supabase
        response = supabase.storage.from_(JD_BUCKETNAME).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )

        # ❌ Handle upload error (new SDK format safe check)
        if hasattr(response, "error") and response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {response.error}"
            )

        # ✅ Get public URL
        public_url = supabase.storage.from_(JD_BUCKETNAME).get_public_url(file_name)

        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )