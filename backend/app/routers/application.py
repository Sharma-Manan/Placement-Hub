from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.models.application import Application
from app.models.student import Student
from app.core.dependencies import require_student, require_coordinator
from app.schemas.application import BulkShortlistRequest


from app.schemas.application import (
    ApplicationOut,
    ApplicationOutStudent,
    ApplicationStatusUpdate
)

from app.crud.application import (
    apply_to_opportunity,
    get_my_applications,
    get_applications_for_opportunity,
    update_application_status
)

application_router = APIRouter(tags=["Applications"])

def notify(student_id, message):
    print(f"Notify {student_id}: {message}")
    
# --------------------------------------------------
# Apply to Opportunity (Student)
# --------------------------------------------------
@application_router.post(
    "/opportunities/{opportunity_id}/apply",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED
)
def apply(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student)
):
    return apply_to_opportunity(
        db=db,
        student_id=current_user.id,
        opportunity_id=opportunity_id
    )



# --------------------------------------------------
# Get My Applications (Student) → UI READY ✅
# --------------------------------------------------
@application_router.get(
    "/applications/me",
    response_model=List[ApplicationOutStudent]
)
def my_applications(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_student)
):
    return get_my_applications(db, student_id=current_user.id)


# --------------------------------------------------
# Get Applications for Opportunity (Coordinator)
# --------------------------------------------------
@application_router.get(
    "/opportunities/{opportunity_id}/applications",
    response_model=List[ApplicationOut]
)
def applications_for_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator)
):
    return get_applications_for_opportunity(db, opportunity_id)


# --------------------------------------------------
# Update Application Status (Coordinator)
# --------------------------------------------------
@application_router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationOut
)
def update_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator)
):
    return update_application_status(db, application_id, payload)



@application_router.post("/opportunities/{opportunity_id}/shortlist")
def bulk_shortlist(
    opportunity_id: str,
    payload: BulkShortlistRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    student_ids = payload.student_ids

    # shortlist selected
    db.query(Application).filter(
        Application.opportunity_id == opportunity_id,
        Application.student_id.in_(student_ids)
    ).update(
        {"status": "shortlisted"},
        synchronize_session=False
    )

    # reject others
    db.query(Application).filter(
        Application.opportunity_id == opportunity_id,
        ~Application.student_id.in_(student_ids)
    ).update(
        {"status": "rejected"},
        synchronize_session=False
    )

    db.commit()   # ✅ IMPORTANT BEFORE NOTIFICATIONS

    # -------------------------
    # ✅ NOTIFICATION BLOCK HERE
    # -------------------------
    selected_ids = set(student_ids)

    all_apps = db.query(Application).filter(
        Application.opportunity_id == opportunity_id
    ).all()

    for app in all_apps:
        if app.student_id in selected_ids:
            notify(app.student_id, "You are shortlisted 🎉")
        else:
            notify(app.student_id, "Not shortlisted")

    return {"message": "Shortlisting completed"}


@application_router.get("/students/search")
def search_students(query: str, db: Session = Depends(get_db)):
    return db.query(Student).filter(
        Student.email.ilike(f"%{query}%")
    ).limit(10).all()