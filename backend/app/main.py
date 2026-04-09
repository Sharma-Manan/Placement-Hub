from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os
from supabase import create_client, Client
from app.core.config import origins, init_cloudinary 
from app.routers.auth import router
from app.routers.profiles import student_profile_create, coordinator_profile_create
from app.routers.company import company_router
from app.routers.upload import upload_router
from app.routers.opportunity import opportunity_router
from app.routers.application import application_router
from app.routers.eligibility import eligibility_router
from app.routers.wall_of_fame import wall_of_fame_router
from app.routers.event import router as event_router
from app.routers.placed_student import router as placed_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_cloudinary()
    print("✅ Cloudinary initialized")

    yield  
    print("🛑 App shutting down")

app = FastAPI(lifespan=lifespan)


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

@app.get("/health")
def health():
    return {"status": "ok"}

    
app.include_router(router)
app.include_router(student_profile_create)
app.include_router(coordinator_profile_create)
app.include_router(company_router)
app.include_router(upload_router)
app.include_router(opportunity_router)
app.include_router(eligibility_router)
app.include_router(application_router)
app.include_router(wall_of_fame_router)
app.include_router(event_router)
app.include_router(placed_router)
