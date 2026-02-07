from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from app.routers.auth import router
from app.routers.profileCreate import student_profile_create, coordinator_profile_create
from app.routers.company import company_router

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/")
def home():
    response = supabase.table("companies").select("*").execute()
    return {"data": response.data}


@app.get("/health")
def health_check():
    try:
        supabase.table("companies").select("id").limit(1).execute()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
app.include_router(router)
app.include_router(student_profile_create)
app.include_router(coordinator_profile_create)
app.include_router(company_router)
