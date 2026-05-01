from fastapi import APIRouter
from app.services.ai_extraction_service import parse_resume_from_url

ai_router = APIRouter()

@ai_router.post("/extract-resume")
async def extract_resume(data: dict):
    resume_url = data.get("resume_url")
    return parse_resume_from_url(resume_url)

@ai_router.get("/my-data")
async def get_my_data():
    return {"message": "placeholder"}