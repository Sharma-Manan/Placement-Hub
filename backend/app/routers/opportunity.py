from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

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
    

@opportunity_router.post("/companies/{company_id}/opportunities",response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    company_id:  UUID,
    payload:     OpportunityCreate,
    db:          Session      = Depends(get_db),
    _:           CurrentUser  = Depends(require_coordinator),
):
    return crud_create_opportunity(db, payload, company_id)

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