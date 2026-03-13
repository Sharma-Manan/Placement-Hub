from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from fastapi import HTTPException

from app.db.session import get_db
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityOut
from app.crud.opportunity import (
    create_opportunity as crud_create_opportunity,
    get_opportunity as crud_get_opportunity,
    get_opportunities as crud_get_opportunities,
    update_opportunity as crud_update_opportunity,
    delete_opportunity as crud_delete_opportunity,
)

opportunity_router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@opportunity_router.post("/", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "coordinator":
        raise HTTPException(status_code=403, detail="Only coordinators can create opportunities")

    return crud_create_opportunity(db, opportunity)


@opportunity_router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity_by_id(opportunity_id: str, db: Session = Depends(get_db)):
    return crud_get_opportunity(db, opportunity_id)


@opportunity_router.get("/", response_model=List[OpportunityOut])
def list_opportunities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_get_opportunities(db, skip=skip, limit=limit)


@opportunity_router.put("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: str,
    opportunity_in: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "coordinator":
        raise HTTPException(status_code=403, detail="Only coordinators can update opportunities")

    return crud_update_opportunity(db, opportunity_id, opportunity_in)


@opportunity_router.delete("/{opportunity_id}", response_model=OpportunityOut)
def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "coordinator":
        raise HTTPException(status_code=403, detail="Only coordinators can delete opportunities")

    return crud_delete_opportunity(db, opportunity_id)