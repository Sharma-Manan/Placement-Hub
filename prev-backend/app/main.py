"""
main.py
This is the entry point of the FastAPI application.
It initializes the app and includes API routers.
"""

from fastapi import FastAPI

app = FastAPI(
    title="AI-Based Smart Placement & Internship Coordination System",
    version="1.0.0" 
)

@app.get("/")
def root():
    return {"status" : "Backend is running"}

from app.core.database import engine

@app.get("/db-test")
def db_test():
    return {"db": str(engine.url)}
