import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "PlaceMind AI"
ENVIRONMENT =  os.getenv("ENVIRONMENT", "development")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))

# CORS


# Email (future)
