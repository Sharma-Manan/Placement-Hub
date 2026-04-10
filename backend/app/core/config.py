import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()

APP_NAME = "PlaceMind AI"
ENVIRONMENT =  os.getenv("ENVIRONMENT", "development")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
JD_BUCKETNAME = os.getenv("SUPABASE_BUCKET", "jd_files")


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
# Password hashing
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))

# Cloudinary

def init_cloudinary():
    cloudinary.config(
        cloud_name="CLOUDINARY_NAME",
        api_key="CLUODINARY_API",
        api_secret="CLUODINARY_API_SECRET",
        secure=True
    )