from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.student import Student
from app.models.coordinator import Coordinator
from app.models.user import User
from app.schemas.profileCreate import StudentProfileCreate  ,  CoordinatorProfileCreate #, CompanyProfileCreate
from app.core.security import get_current_user

student_profile_create = APIRouter(prefix="/student", tags=["Student"])
coordinator_profile_create = APIRouter(prefix="/coordinator", tags=["Coordinator"])


@student_profile_create.post("/profile")
def create_student_profile(
    payload: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")

    # check if profile exists
    existing = db.query(Student).filter_by(user_id=current_user.id).first()

    if existing:
        # Update the existing profile
        for key, value in payload.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return {"message": "Student profile updated", "profile": existing}

    # Create new profile
    student = Student(user_id=current_user.id, **payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)

    return {"message": "Student profile created", "profile": student}



@coordinator_profile_create.post("/profile")
def create_coordinator_profile(
    payload: CoordinatorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "coordinator":
        raise HTTPException(status_code=403, detail="Not a coordinator")
    
    existing = db.query(Coordinator).filter_by(user_id=current_user.id).first()

    if existing:
        for key, value in payload.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return {"message": "Coordinator profile updated", "profile": existing}        

    coordinator = Coordinator(user_id=current_user.id, **payload.model_dump())
    db.add(coordinator)
    db.commit()
    db.refresh(coordinator)

    return {"message": "Coordinator profile created", "profile": coordinator}