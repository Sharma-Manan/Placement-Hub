from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from app.core.config import SUPABASE_URL, SUPABASE_KEY, DATABASE_URL

load_dotenv()
# --------------------------------------------------
# Database URL (Supabase PostgreSQL)
# --------------------------------------------------
# Format:
# postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE

DATABASE_URL = os.getenv("DATABASE_URL")


# --------------------------------------------------
# SQLAlchemy Engine & Session
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)




# --------------------------------------------------
# Dependency
# --------------------------------------------------

def get_db():
    """
    FastAPI dependency that provides a database session.
    Ensures the session is closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
