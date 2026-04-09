# from fastapi import APIRouter, Depends, HTTPException,UploadFile, File
# from sqlalchemy.orm import Session
# from datetime import timedelta

# from app.db.session import get_db
# from app.models.student import Student
# from app.models.coordinator import Coordinator
# from app.models.opportunity import Opportunity

# from app.services.cloudinary_service import CloudinaryService
# from app.schemas.profiles import StudentProfileCreate, CoordinatorProfileCreate
# from app.schemas.placed_student import PlacedStudentListOut
# from app.schemas.auth import CurrentUser

# from app.core.dependencies import require_coordinator, require_student
# from app.crud.placed_students import get_all_placed_students
# from app.services.conflict_service import get_student_conflicts
# from app.schemas.profiles import StudentProfileOut

# student_profile_create = APIRouter(prefix="/student", tags=["Student"])
# coordinator_profile_create = APIRouter(prefix="/coordinator", tags=["Coordinator"])


# @student_profile_create.post("/profile")
# def upsert_student_profile(
#     payload: StudentProfileCreate,
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_student),
# ):
#     data = payload.model_dump()

#     for field in ["resume_url", "linkedin_url", "github_url", "portfolio_url"]:
#         if field in data and data[field]:
#             data[field] = str(data[field])

#     existing = db.query(Student).filter_by(user_id=current_user.id).first()

#     if existing:
#         for key, value in data.items():
#             setattr(existing, key, value)
#         db.commit()
#         db.refresh(existing)
#         return {"message": "Student profile updated", "profile": existing}

#     student = Student(user_id=current_user.id, **data)
#     db.add(student)
#     db.commit()
#     db.refresh(student)
#     return {"message": "Student profile created", "profile": student}


# @student_profile_create.get("/profile", response_model=StudentProfileOut)
# def get_student_profile(
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_student),
# ):
#     student = db.query(Student).filter_by(user_id=current_user.id).first()

#     if not student:
#         raise HTTPException(status_code=404, detail="Student profile not found")
#     return student


# @student_profile_create.patch("/profile/photo")
# async def update_student_profile_photo(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_student)
# ):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image files allowed")

#     contents = await file.read()
#     if len(contents) > 2 * 1024 * 1024:
#         raise HTTPException(status_code=400, detail="File too large (max 2MB)")

#     file.file.seek(0)

#     student = db.query(Student).filter_by(user_id=current_user.id).first()

#     if not student:
#         raise HTTPException(status_code=404, detail="Student profile not found")

#     if student.profile_photo_public_id:
#         CloudinaryService.delete_image(student.profile_photo_public_id)

#     upload_result = CloudinaryService.upload_image(file.file)

#     student.profile_photo_url = upload_result["url"]
#     student.profile_photo_public_id = upload_result["public_id"]

#     db.commit()
#     db.refresh(student)

#     return {
#         "profile_photo_url": student.profile_photo_url
#     }

# @student_profile_create.get("/conflicts")
# def get_conflicts(
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_student),
# ):
#     student = db.query(Student).filter_by(user_id=current_user.id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Student profile not found")

#     conflicts = get_student_conflicts(db, student.id)

#     opportunity_ids = set()
#     for event1, event2 in conflicts:
#         opportunity_ids.add(event1.opportunity_id)
#         opportunity_ids.add(event2.opportunity_id)

#     opportunities = db.query(Opportunity).filter(
#         Opportunity.id.in_(opportunity_ids)
#     ).all()

#     opp_map = {opp.id: opp for opp in opportunities}

#     response = []
#     for event1, event2 in conflicts:
#         opp1 = opp_map.get(event1.opportunity_id)
#         opp2 = opp_map.get(event2.opportunity_id)

#         response.append(
#             {
#                 "event_1": {
#                     "event_id": event1.id,
#                     "company_name": opp1.company_name if opp1 else None,
#                     "event_type": event1.event_type,
#                     "start_time": event1.event_datetime,
#                     "end_time": event1.event_datetime
#                     + timedelta(minutes=event1.duration_minutes),
#                 },
#                 "event_2": {
#                     "event_id": event2.id,
#                     "company_name": opp2.company_name if opp2 else None,
#                     "event_type": event2.event_type,
#                     "start_time": event2.event_datetime,
#                     "end_time": event2.event_datetime
#                     + timedelta(minutes=event2.duration_minutes),
#                 },
#             }
#         )

#     return {
#         "total_conflicts": len(response),
#         "conflicts": response,
#     }


# @coordinator_profile_create.post("/profile")
# def create_coordinator_profile(
#     payload: CoordinatorProfileCreate,
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_coordinator),
# ):
#     existing = db.query(Coordinator).filter_by(user_id=current_user.id).first()

#     if existing:
#         for key, value in payload.model_dump().items():
#             setattr(existing, key, value)
#         db.commit()
#         db.refresh(existing)
#         return {"message": "Coordinator profile updated", "profile": existing}

#     coordinator = Coordinator(user_id=current_user.id, **payload.model_dump())
#     db.add(coordinator)
#     db.commit()
#     db.refresh(coordinator)
#     return {"message": "Coordinator profile created", "profile": coordinator}


# @coordinator_profile_create.get("/profile")
# async def get_coordinator_profile(
#     current_user: CurrentUser = Depends(require_coordinator),
# ):
#     return {
#         "first_name": current_user.first_name,
#         "last_name": current_user.last_name,
#         "is_primary": current_user.is_primary,
#         "profile_photo_url": current_user.profile_photo_url,
#     }

# @coordinator_profile_create.patch("/profile/photo")
# async def update_coordinator_profile_photo(
#     payload: dict,
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_coordinator)
# ):
#     coordinator = db.query(Coordinator).filter_by(user_id=current_user.id).first()

#     if not coordinator:
#         raise HTTPException(status_code=404, detail="Coordinator profile not found")

#     coordinator.profile_photo_url = payload.get("profile_photo_url")

#     db.commit()
#     db.refresh(coordinator)

#     return {"profile_photo_url": coordinator.profile_photo_url}



# @coordinator_profile_create.patch("/admin/photo")
# async def update_admin_photo(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_coordinator)
# ):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image files allowed")

#     contents = await file.read()
#     if len(contents) > 2 * 1024 * 1024:
#         raise HTTPException(status_code=400, detail="File too large (max 2MB)")

#     file.file.seek(0)

#     admin = db.query(Coordinator).filter_by(id=current_user.id).first()

#     if not admin:
#         raise HTTPException(status_code=404, detail="Admin not found")

#     if admin.profile_photo_public_id:
#         CloudinaryService.delete_image(admin.profile_photo_public_id)

#     upload_result = CloudinaryService.upload_image(
#         file.file,
#         folder="admin_photos"
#     )

#     admin.profile_photo_url = upload_result["url"]
#     admin.profile_photo_public_id = upload_result["public_id"]

#     db.commit()
#     db.refresh(admin)

#     return {
#         "profile_photo_url": admin.profile_photo_url
#     }



# @coordinator_profile_create.get(
#     "/placed", response_model=list[PlacedStudentListOut]
# )
# def list_placed_students(
#     skip: int = 0,
#     limit: int = 50,
#     db: Session = Depends(get_db),
#     current_user: CurrentUser = Depends(require_coordinator),
# ):
#     return get_all_placed_students(db, skip, limit)


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.db.session import get_db
from app.models.student import Student
from app.models.coordinator import Coordinator
from app.models.opportunity import Opportunity
from app.models.application import Application
from app.models.eligibility_rules import EligibilityRules

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


@student_profile_create.get("/opportunities")
def get_student_opportunities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student),
):
    """
    Returns opportunities enriched with:
    - is_eligible: Boolean indicating if student meets eligibility criteria
    - has_applied: Boolean indicating if student has already applied
    - ineligible_reason: String explaining why student is not eligible (if applicable)
    """
    
    # 1. Get student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please complete your profile first."
        )
    
    # 2. Get all active opportunities
    opportunities = db.query(Opportunity).filter(
        Opportunity.status == "active",
        Opportunity.application_deadline > datetime.utcnow()
    ).offset(skip).limit(limit).all()
    
    # 3. Enrich each opportunity with student-specific data
    result = []

    for opp in opportunities:
        # Check if student has already applied
        existing_application = db.query(Application).filter(
            Application.student_id == student.id,
            Application.opportunity_id == opp.id
        ).first()

        has_applied = existing_application is not None

        # Check eligibility
        is_eligible = True
        ineligible_reason = None

        # ✅ Fetch rules properly (NOT opp.eligibility)
        rules = db.query(EligibilityRules).filter(
            EligibilityRules.opportunity_id == opp.id
        ).first()

        if rules:
            # CGPA Check
            if rules.min_cgpa is not None:
                if student.cgpa < rules.min_cgpa:
                    is_eligible = False
                    ineligible_reason = f"Minimum CGPA {rules.min_cgpa} required (You have {student.cgpa})"

            # Backlogs Check
            if rules.max_backlogs is not None and is_eligible:
                if student.active_backlogs > rules.max_backlogs:
                    is_eligible = False
                    ineligible_reason = f"Maximum {rules.max_backlogs} backlogs allowed (You have {student.active_backlogs})"

            # Department Check
            if rules.allowed_depts and is_eligible:
                if student.department_id not in rules.allowed_depts:
                    is_eligible = False
                    ineligible_reason = f"Only {', '.join(rules.allowed_depts)} departments are eligible"

            # Batch Check
            if rules.allowed_batches and is_eligible:
                if student.graduation_year not in rules.allowed_batches:
                    is_eligible = False
                    ineligible_reason = f"Only batches {', '.join(map(str, rules.allowed_batches))} are eligible"

            # Prior Offer Check
            if rules.no_prior_offer and is_eligible:
                if student.placement_status != "unplaced":
                    is_eligible = False
                    ineligible_reason = "Only unplaced students can apply"
        
        # Build response object
        opp_dict = {
            "id": opp.id,
            "title": opp.title,
            "company_id": opp.company_id,
            "company_name": opp.company_name,
            "description": opp.description,
            "location": opp.location,
            "ctc_lpa": opp.ctc_lpa,
            "application_deadline": opp.application_deadline,
            "status": opp.status,
            "created_at": opp.created_at,
            "updated_at": opp.updated_at,

            # student-specific
            "has_applied": has_applied,
            "is_eligible": is_eligible,
            "ineligible_reason": ineligible_reason,
        }
        
        result.append(opp_dict)
    
    return result


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



@coordinator_profile_create.patch("/admin/photo")
async def update_admin_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    file.file.seek(0)

    admin = db.query(Coordinator).filter_by(id=current_user.id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if admin.profile_photo_public_id:
        CloudinaryService.delete_image(admin.profile_photo_public_id)

    upload_result = CloudinaryService.upload_image(
        file.file,
        folder="admin_photos"
    )

    admin.profile_photo_url = upload_result["url"]
    admin.profile_photo_public_id = upload_result["public_id"]

    db.commit()
    db.refresh(admin)

    return {
        "profile_photo_url": admin.profile_photo_url
    }



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