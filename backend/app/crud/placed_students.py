from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status

from app.models.placed_student import PlacedStudent
from app.models.student import Student


def get_all_placed_students(db: Session, skip: int = 0, limit: int = 50):
    return (
        db.query(Student).filter(Student.placement_status.in_(["placed", "offer_received"]))
        .offset(skip)
        .limit(limit)
        .all()
            )