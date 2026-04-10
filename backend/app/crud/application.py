from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone

from app.models.application import Application
from app.models.opportunity import Opportunity
from app.models.student import Student
from app.models.company import Company 
from app.models.user import User

from app.schemas.application import ApplicationStatusUpdate

from app.services.eligibility import check_eligibility
from app.models.student import Student
from app.models.placed_student import PlacedStudent
from app.services.notification_service import notify_student, notify_all_coordinators
from app.models.notification import NotificationType


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
    
    # 🔥 Block if already accepted an offer
    if student.placement_status != "unplaced":
        raise HTTPException(
            status_code=400,
            detail="You have already accepted an offer"
        )
    
    #  Get user (for email)
    user = db.query(User).filter(User.id == student.user_id).first()

    # 4. Check duplicate application (FIXED)
    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.opportunity_id == opportunity_id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already applied to this opportunity")

    # 5. Eligibility check
    is_eligible, reason = check_eligibility(student, opportunity, db)

    if not is_eligible:
        raise HTTPException(
            status_code=403,
            detail=reason
        )

    # 6. Create application
    application = Application(
        student_id=student.id,
        opportunity_id=opportunity_id,
        status="applied",
        student_name=f"{student.first_name} {student.last_name}",
        student_email=user.email,  
        student_cgpa=str(student.cgpa) if student.cgpa else None,
        student_department=student.department_id,
        student_resume_url=student.resume_url or None 
    )

    db.add(application)
    db.commit()
    db.refresh(application)

     # ── NOTIFICATIONS ──────────────────────────────

    # 1. Notify student: application submitted successfully
    notify_student(
        db=db,
        user_id=student.user_id,
        type=NotificationType.APPLICATION_SUBMITTED,
        title="Application Submitted",
        message=f"Your application for {opportunity.title} at {opportunity.company_name} has been submitted successfully.",
        related_opportunity_id=opportunity.id,
        related_application_id=application.id,
    )

    # 2. Notify all coordinators: new application received
    notify_all_coordinators(
        db=db,
        type=NotificationType.NEW_APPLICATION,
        title="New Application Received",
        message=f"{student.first_name} {student.last_name} applied for {opportunity.title} at {opportunity.company_name}.",
        related_opportunity_id=opportunity.id,
        related_application_id=application.id,
    )

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
            "company_name": opportunity.company_name, 
            "application_deadline": opportunity.application_deadline
        })

    return result


# --------------------------------------------------
# Get Applications for Opportunity (Coordinator)
# --------------------------------------------------
def get_applications_for_opportunity(db: Session, opportunity_id: str):
    applications = db.query(Application).filter(
        Application.opportunity_id == opportunity_id
    ).all()

    result = []

    for app in applications:
        result.append({
            "id": app.id,
            "opportunity_id": app.opportunity_id,

            #  Student Snapshot
            "student_name": app.student_name,
            "student_email": app.student_email,
            "student_cgpa": app.student_cgpa,
            "student_department": app.student_department,
            "student_resume_url": app.student_resume_url, 

            "status": app.status,
            "created_at": app.created_at
        })

    return result


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

    #  If student accepted → mark in student table
    if payload.status == "accepted":
        student = db.query(Student).filter(Student.id == application.student_id).first()
        if student:
            student.has_accepted_offer = True
            student.placement_status = "placed"

    # 2. Check duplicate (important)
    existing = db.query(PlacedStudent).filter(
        PlacedStudent.application_id == application.id
    ).first()

    if not existing:

        # 3. Get opportunity (for company + role)
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == application.opportunity_id
        ).first()

        if not opportunity:
            raise HTTPException(
                status_code=400,
                detail="Opportunity not found for this application"
            )

        placed = PlacedStudent(
            student_id=application.student_id,
            opportunity_id=application.opportunity_id,
            application_id=application.id,
            company_name=opportunity.company_name if opportunity else "Unknown",
            role=opportunity.title if opportunity else "Unknown",
            ctc_lpa=opportunity.ctc_lpa if opportunity else None
        )

        db.add(placed)

    db.commit()
    db.refresh(application)

     # ── NOTIFICATIONS ──────────────────────────────

    # Get student user_id for notification
    student = db.query(Student).filter(Student.id == application.student_id).first()
    opportunity = db.query(Opportunity).filter(Opportunity.id == application.opportunity_id).first()

    if student and opportunity:

        if payload.status == "shortlisted":
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.STATUS_SHORTLISTED,
                title="You've Been Shortlisted! 🎉",
                message=f"Congratulations! You have been shortlisted for {opportunity.title} at {opportunity.company_name}.",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

        elif payload.status == "rejected":
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.STATUS_REJECTED,
                title="Application Update",
                message=f"Your application for {opportunity.title} at {opportunity.company_name} was not selected this time.",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

        elif payload.status == "test_scheduled":
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.STATUS_TEST_SCHEDULED,
                title="Test Scheduled 📝",
                message=f"A test has been scheduled for {opportunity.title} at {opportunity.company_name}. Check your schedule.",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

        elif payload.status == "interviewed":
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.STATUS_INTERVIEW_SCHEDULED,
                title="Interview Scheduled 🗓️",
                message=f"An interview has been scheduled for {opportunity.title} at {opportunity.company_name}. Best of luck!",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

        elif payload.status == "offered":
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.OFFER_RECEIVED,
                title="Offer Received! 🎁",
                message=f"You have received an offer from {opportunity.company_name} for {opportunity.title}.",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

        elif payload.status == "accepted":
            # Notify student: offer accepted
            notify_student(
                db=db,
                user_id=student.user_id,
                type=NotificationType.OFFER_ACCEPTED,
                title="Offer Accepted! 🎊",
                message=f"You have successfully accepted the offer from {opportunity.company_name}. Congratulations!",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

            # Notify all coordinators: student accepted offer
            notify_all_coordinators(
                db=db,
                type=NotificationType.STUDENT_OFFER_ACCEPTED,
                title="Student Accepted Offer 🏆",
                message=f"{student.first_name} {student.last_name} has accepted the offer from {opportunity.company_name} for {opportunity.title}.",
                related_opportunity_id=opportunity.id,
                related_application_id=application.id,
            )

    return application