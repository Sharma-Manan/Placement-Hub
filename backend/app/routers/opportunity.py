from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timezone
from app.utils.supabase_storage import upload_to_supabase


from app.models.student import Student
from app.models.opportunity import Opportunity
from app.models.application import Application
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.core.dependencies import require_coordinator, require_student
from app.db.session import get_db
from app.schemas.opportunity import (OpportunityCreate, OpportunityUpdate, OpportunityOut, OpportunityOutStudent)
from app.models.eligibility_rules import EligibilityRules
from app.crud.opportunity import (
    create_opportunity as crud_create_opportunity,
    get_opportunity as crud_get_opportunity,
    get_opportunities as crud_get_opportunities,
    # get_eligible_opportunities as crud_get_eligible_opportunities,
    update_opportunity as crud_update_opportunity,
    delete_opportunity as crud_delete_opportunity,
)

opportunity_router = APIRouter(tags=["Opportunities"])
    

from fastapi import UploadFile, File
from app.utils.supabase_storage import upload_to_supabase

@opportunity_router.post(
    "/opportunities",
    response_model=OpportunityOut,
    status_code=status.HTTP_201_CREATED
)
def create_opportunity(
    payload: OpportunityCreate = Depends(OpportunityCreate.as_form),   # 🔥 important
    jd_file: UploadFile = File(None),         # 🔥 file input
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_coordinator),
):
    jd_url = None

    if jd_file:
        jd_url = upload_to_supabase(jd_file)

    return crud_create_opportunity(db, payload, jd_url)

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


# Add this import at the top of your file
from fastapi.responses import JSONResponse
import json

@opportunity_router.get(
    "/student/opportunities",
    summary="Get Opportunities for Student",
    # NO response_model here
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
    
    now = datetime.now(timezone.utc)
    
    # 2. Get all active opportunities
    opportunities = db.query(Opportunity).filter(
        Opportunity.status == "active",
        Opportunity.application_deadline > now
    ).offset(skip).limit(limit).all()
    
    # 3. Enrich each opportunity with student-specific data
    result = []
    
    from app.models.eligibility_rules import EligibilityRules

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

        # Fetch rules
        rules = db.query(EligibilityRules).filter(
            EligibilityRules.opportunity_id == opp.id
        ).first()

        if rules:
            if rules.min_cgpa is not None and float(student.cgpa) < float(rules.min_cgpa):
                is_eligible = False
                ineligible_reason = f"Minimum CGPA {rules.min_cgpa} required (You have {student.cgpa})"

            if rules.max_backlogs is not None and is_eligible and student.active_backlogs > rules.max_backlogs:
                is_eligible = False
                ineligible_reason = f"Maximum {rules.max_backlogs} backlogs allowed (You have {student.active_backlogs})"
        
        # Build response object - EXPLICITLY include all fields
        opp_dict = {
            "id": str(opp.id),
            "title": opp.title,
            "company_id": str(opp.company_id) if opp.company_id else None,
            "company_name": opp.company_name,
            "description": opp.description,
            "location": opp.location,
            "ctc_lpa": float(opp.ctc_lpa) if opp.ctc_lpa is not None else None,
            "application_deadline": opp.application_deadline.isoformat() if opp.application_deadline else None,
            "status": opp.status,
            "created_at": opp.created_at.isoformat() if opp.created_at else None,
            "updated_at": opp.updated_at.isoformat() if opp.updated_at else None,
            
            # ✅ THESE 4 FIELDS YOU WANTED
            "company_logo": opp.company_logo,
            "company_url": opp.company_url,
            "jd_url": opp.jd_url,
            "additional_criteria": opp.additional_criteria,
            
            # Eligibility object
            "eligibility": {
                "min_cgpa": float(rules.min_cgpa) if rules and rules.min_cgpa else None,
                "max_backlogs": rules.max_backlogs if rules else None,
                "allowed_depts": rules.allowed_depts if rules else [],
                "allowed_batches": rules.allowed_batches if rules else [],
                "no_prior_offer": rules.no_prior_offer if rules else False,
            } if rules else None,

            # student-specific
            "has_applied": has_applied,
            "is_eligible": is_eligible,
            "ineligible_reason": ineligible_reason,
        }
        
        result.append(opp_dict)
    
    # DEBUG: Print to terminal to verify
    if result:
        print("\n" + "="*80)
        print("DEBUG: FIRST OPPORTUNITY BEING SENT TO FRONTEND")
        print("="*80)
        print(json.dumps(result[0], indent=2, default=str))
        print("="*80 + "\n")
    
    # ✅ Return as JSONResponse to bypass any Pydantic filtering
    return JSONResponse(content=result)


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

