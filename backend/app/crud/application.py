from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone

from app.models.application import Application
from app.models.opportunity import Opportunity
from app.models.student import Student
from app.models.company import Company 

from app.schemas.application import ApplicationStatusUpdate

from app.services.eligibility import check_eligibility


# --------------------------------------------------
# Apply to Opportunity
# --------------------------------------------------
def apply_to_opportunity(db: Session, student_id: str, opportunity_id: str) -> Application:

    # 1. Check opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # 2. Check deadline
    if opportunity.application_deadline and opportunity.application_deadline < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Application deadline has passed")

    # 3. Get student (user_id → student.id)
    student = db.query(Student).filter(Student.user_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 4. Check duplicate application (FIXED)
    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.opportunity_id == opportunity_id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already applied to this opportunity")

    # 5. Eligibility check
    is_eligible = check_eligibility(student, opportunity,db)
    if not is_eligible:
        raise HTTPException(status_code=403, detail="You are not eligible for this opportunity")

    # 6. Create application
    application = Application(
        student_id=student.id,
        opportunity_id=opportunity_id,
        status="applied"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


# --------------------------------------------------
# Get My Applications (Student) → UI READY ✅
# --------------------------------------------------
def get_my_applications(db: Session, student_id: str):

    student = db.query(Student).filter(Student.user_id == student_id).first()

    if not student:
        return []

    applications = db.query(Application).filter(
        Application.student_id == student.id
    ).all()

    result = []

    for app in applications:
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == app.opportunity_id
        ).first()

        # 🔥 FIX: fetch company manually
        company = db.query(Company).filter(
            Company.id == opportunity.company_id
        ).first()

        result.append({
            "id": app.id,
            "status": app.status,
            "created_at": app.created_at,
            "opportunity_id": opportunity.id,
            "opportunity_title": opportunity.title,
            "company_name": company.name if company else None,
            "application_deadline": opportunity.application_deadline
        })

    return result


# --------------------------------------------------
# Get Applications for Opportunity (Coordinator)
# --------------------------------------------------
def get_applications_for_opportunity(db: Session, opportunity_id: str):
    return db.query(Application).filter(
        Application.opportunity_id == opportunity_id
    ).all()


# --------------------------------------------------
# Update Application Status (Coordinator)
# --------------------------------------------------
def update_application_status(
    db: Session,
    application_id: str,
    payload: ApplicationStatusUpdate
) -> Application:

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = payload.status

    db.commit()
    db.refresh(application)

    return application