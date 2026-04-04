from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.student import Student
from app.models.coordinator import Coordinator
from app.models.user import User
from app.models.opportunity import Opportunity
from app.schemas.profiles import StudentProfileCreate, CoordinatorProfileCreate
from app.schemas.placed_student import PlacedStudentListOut
from app.schemas.auth import CurrentUser
from app.core.security import get_current_user
from app.core.dependencies import require_coordinator
from app.crud.placed_students import get_all_placed_students
from app.services.conflict_service import get_student_conflicts


student_profile_create = APIRouter(prefix="/student", tags=["Student"])
coordinator_profile_create = APIRouter(prefix="/coordinator", tags=["Coordinator"])


@student_profile_create.post("/profile")
def upsert_student_profile(
    payload: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")

    data = payload.model_dump()
    for field in ["resume_url", "linkedin_url", "github_url", "portfolio_url"]:
        if field in data and data[field]:
            data[field] = str(data[field])

    existing = db.query(Student).filter_by(user_id=current_user.id).first()

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return {"message": "Student profile updated", "profile": existing}

    student = Student(user_id=current_user.id, **data)
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


@coordinator_profile_create.get("/placed", response_model=list[PlacedStudentListOut])
def list_placed_students(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    return get_all_placed_students(db, skip, limit)


@student_profile_create.get("/conflicts")
def get_conflicts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not a student")

    student = db.query(Student).filter_by(user_id=current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    conflicts = get_student_conflicts(db, student.id)

    opportunity_ids = set()
    for event1, event2 in conflicts:
        opportunity_ids.add(event1.opportunity_id)
        opportunity_ids.add(event2.opportunity_id)

    opportunities = db.query(Opportunity).filter(
        Opportunity.id.in_(opportunity_ids)
    ).all()

    opp_map = {opp.id: opp for opp in opportunities}

    response = []
    for event1, event2 in conflicts:
        opp1 = opp_map.get(event1.opportunity_id)
        opp2 = opp_map.get(event2.opportunity_id)

        response.append({
            "event_1": {
                "event_id": event1.id,
                "company_name": opp1.company_name if opp1 else None,
                "event_type": event1.event_type,
                "start_time": event1.event_datetime,
                "end_time": event1.event_datetime + timedelta(minutes=event1.duration_minutes),
            },
            "event_2": {
                "event_id": event2.id,
                "company_name": opp2.company_name if opp2 else None,
                "event_type": event2.event_type,
                "start_time": event2.event_datetime,
                "end_time": event2.event_datetime + timedelta(minutes=event2.duration_minutes),
            }
        })

    return {
        "total_conflicts": len(response),
        "conflicts": response
    }