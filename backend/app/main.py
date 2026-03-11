from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client
from app.core.config import origins
from app.routers.auth import router
from app.routers.profileCreate import student_profile_create, coordinator_profile_create
from app.routers.company import company_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



@app.get("/debug-cors")
def debug_cors():
    return {"origins": origins}

    
app.include_router(router)
app.include_router(student_profile_create)
app.include_router(coordinator_profile_create)
app.include_router(company_router)
