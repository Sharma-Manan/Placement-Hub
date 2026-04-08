from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.application import Application
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.core.dependencies import require_coordinator, require_student
from app.db.session import get_db
from app.schemas.opportunity import (OpportunityCreate, OpportunityUpdate, OpportunityOut, OpportunityOutStudent)
from app.crud.opportunity import (
    create_opportunity as crud_create_opportunity,
    get_opportunity as crud_get_opportunity,
    get_opportunities as crud_get_opportunities,
    # get_eligible_opportunities as crud_get_eligible_opportunities,
    update_opportunity as crud_update_opportunity,
    delete_opportunity as crud_delete_opportunity,
)

opportunity_router = APIRouter(tags=["Opportunities"])
    

@opportunity_router.post(
    "/opportunities",
    response_model=OpportunityOut,
    status_code=status.HTTP_201_CREATED
)
def create_opportunity(
    payload: OpportunityCreate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_coordinator),
):
    return crud_create_opportunity(db, payload)


@opportunity_router.patch(
    "/opportunities/{opportunity_id}",
    response_model=OpportunityOut,
)
def update_opportunity(
    opportunity_id: UUID,
    payload:        OpportunityUpdate,
    db:             Session     = Depends(get_db),
    _:              CurrentUser = Depends(require_coordinator),
):
    return crud_update_opportunity(db, opportunity_id, payload)


@opportunity_router.delete(
    "/opportunities/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # delete returns no body
)
def delete_opportunity(
    opportunity_id: UUID,
    db:             Session     = Depends(get_db),
    _:              CurrentUser = Depends(require_coordinator),
):
    crud_delete_opportunity(db, opportunity_id)



@opportunity_router.get(
    "/student/opportunities",
    response_model=List[OpportunityOutStudent],
    summary="Get Opportunities for Student",
    description="Returns all active opportunities with eligibility check and application status for the logged-in student"
)
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
        Opportunity.is_accepting_applications == True
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
        
        if opp.eligibility:
            # CGPA Check
            min_cgpa = opp.eligibility.get("min_cgpa")
            if min_cgpa is not None:
                if student.cgpa < min_cgpa:
                    is_eligible = False
                    ineligible_reason = f"Minimum CGPA {min_cgpa} required (You have {student.cgpa})"
            
            # Backlogs Check
            max_backlogs = opp.eligibility.get("max_backlogs")
            if max_backlogs is not None and is_eligible:
                if student.active_backlogs > max_backlogs:
                    is_eligible = False
                    ineligible_reason = f"Maximum {max_backlogs} backlogs allowed (You have {student.active_backlogs})"
            
            # Department Check
            allowed_depts = opp.eligibility.get("allowed_depts", [])
            if allowed_depts and is_eligible:
                if student.department_id not in allowed_depts:
                    is_eligible = False
                    ineligible_reason = f"Only {', '.join(allowed_depts)} departments are eligible"
            
            # Batch/Graduation Year Check
            allowed_batches = opp.eligibility.get("allowed_batches", [])
            if allowed_batches and is_eligible:
                if student.graduation_year not in allowed_batches:
                    is_eligible = False
                    ineligible_reason = f"Only batches {', '.join(map(str, allowed_batches))} are eligible"
            
            # Prior Offer Check
            no_prior_offer = opp.eligibility.get("no_prior_offer", False)
            if no_prior_offer and is_eligible:
                if student.placement_status == "placed":
                    is_eligible = False
                    ineligible_reason = "Only unplaced students can apply"
        
        # Build response object
        opp_dict = {
            "id": str(opp.id),
            "title": opp.title,
            "company_name": opp.company_name,
            "description": opp.description,
            "location": opp.location,
            "ctc_lpa": opp.ctc_lpa,
            "application_deadline": opp.application_deadline,
            "eligibility": opp.eligibility,
            "is_accepting_applications": opp.is_accepting_applications,
            "created_at": opp.created_at,
            "updated_at": opp.updated_at,
            # Student-specific fields
            "has_applied": has_applied,
            "is_eligible": is_eligible,
            "ineligible_reason": ineligible_reason,
        }
        
        result.append(opp_dict)
    
    return result

@opportunity_router.get(
    "/opportunities",
    response_model=List[OpportunityOut],
)
def list_all_opportunities(
    skip: int = 0,
    limit: int = 10,
    db:   Session     = Depends(get_db),
    _:    CurrentUser = Depends(require_coordinator),  # coordinator sees all
):
    return crud_get_opportunities(db, skip=skip, limit=limit)


# ── shared routes (coordinator + student) ────────────────────────

@opportunity_router.get(
    "/opportunities/{opportunity_id}",
    response_model=OpportunityOut,
)
def get_opportunity_by_id(
    opportunity_id: UUID,
    db:             Session     = Depends(get_db),
    current_user:   CurrentUser = Depends(get_current_user),   # any logged in user
):
    return crud_get_opportunity(db, opportunity_id)


# ── student-only routes ───────────────────────────────────────────

# @opportunity_router.get(
#     "/opportunities/eligible",
#     response_model=List[OpportunityOutStudent],
# )
# def get_eligible_opportunities(
#     db:           Session     = Depends(get_db),
#     current_user: CurrentUser = Depends(get_current_user),
# ):
#     if current_user.role != "student":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only students can access eligible opportunities"
#         )
#     return crud_get_eligible_opportunities(db, current_user.id)9+