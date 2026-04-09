from fastapi import APIRouter, Depends, HTTPException,UploadFile, File
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.student import Student
from app.models.coordinator import Coordinator
from app.models.opportunity import Opportunity

from app.services.cloudinary_service import CloudinaryService
from app.schemas.profiles import StudentProfileCreate, CoordinatorProfileCreate
from app.schemas.placed_student import PlacedStudentListOut
from app.schemas.auth import CurrentUser

from app.core.dependencies import require_coordinator, require_student
from app.crud.placed_students import get_all_placed_students
from app.services.conflict_service import get_student_conflicts
from app.schemas.profiles import StudentProfileOut

student_profile_create = APIRouter(prefix="/student", tags=["Student"])
coordinator_profile_create = APIRouter(prefix="/coordinator", tags=["Coordinator"])


@student_profile_create.post("/profile")
def upsert_student_profile(
    payload: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
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


@student_profile_create.get("/profile", response_model=StudentProfileOut)
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
    student = db.query(Student).filter_by(user_id=current_user.id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


@student_profile_create.patch("/profile/photo")
async def update_student_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    file.file.seek(0)

    student = db.query(Student).filter_by(user_id=current_user.id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if student.profile_photo_public_id:
        CloudinaryService.delete_image(student.profile_photo_public_id)

    upload_result = CloudinaryService.upload_image(file.file)

    student.profile_photo_url = upload_result["url"]
    student.profile_photo_public_id = upload_result["public_id"]

    db.commit()
    db.refresh(student)

    return {
        "profile_photo_url": student.profile_photo_url
    }

@student_profile_create.get("/conflicts")
def get_conflicts(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
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

        response.append(
            {
                "event_1": {
                    "event_id": event1.id,
                    "company_name": opp1.company_name if opp1 else None,
                    "event_type": event1.event_type,
                    "start_time": event1.event_datetime,
                    "end_time": event1.event_datetime
                    + timedelta(minutes=event1.duration_minutes),
                },
                "event_2": {
                    "event_id": event2.id,
                    "company_name": opp2.company_name if opp2 else None,
                    "event_type": event2.event_type,
                    "start_time": event2.event_datetime,
                    "end_time": event2.event_datetime
                    + timedelta(minutes=event2.duration_minutes),
                },
            }
        )

    return {
        "total_conflicts": len(response),
        "conflicts": response,
    }


@coordinator_profile_create.post("/profile")
def create_coordinator_profile(
    payload: CoordinatorProfileCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
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


@coordinator_profile_create.get("/profile")
async def get_coordinator_profile(
    current_user: CurrentUser = Depends(require_coordinator),
):
    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_primary": current_user.is_primary,
        "profile_photo_url": current_user.profile_photo_url,
    }

@coordinator_profile_create.patch("/profile/photo")
async def update_coordinator_profile_photo(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator)
):
    coordinator = db.query(Coordinator).filter_by(user_id=current_user.id).first()

    if not coordinator:
        raise HTTPException(status_code=404, detail="Coordinator profile not found")

    coordinator.profile_photo_url = payload.get("profile_photo_url")

    db.commit()
    db.refresh(coordinator)

    return {"profile_photo_url": coordinator.profile_photo_url}

@coordinator_profile_create.get(
    "/placed", response_model=list[PlacedStudentListOut]
)
def list_placed_students(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    return get_all_placed_students(db, skip, limit)