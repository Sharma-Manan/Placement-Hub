from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.eligibility_rules import EligibilityRules
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.eligibility_rules import EligibilityRulesCreate, EligibilityRulesUpdate
from app.core.dependencies import require_coordinator

eligibility_router = APIRouter(prefix="/opportunities", tags=["Eligibility"])


@eligibility_router.post("/{opportunity_id}/eligibility", status_code=status.HTTP_201_CREATED)
def create_eligibility_rules(
    opportunity_id: UUID,
    payload: EligibilityRulesCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_coordinator),
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    existing = db.query(EligibilityRules).filter(
        EligibilityRules.opportunity_id == opportunity_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Eligibility rules already exist. Use PATCH to update."
        )

    rules = EligibilityRules(**payload.model_dump(), opportunity_id=opportunity_id)
    db.add(rules)
    db.commit()
    db.refresh(rules)

    return {"message": "Eligibility rules created", "eligibility": rules}


@eligibility_router.patch("/{opportunity_id}/eligibility")
def update_eligibility_rules(
    opportunity_id: UUID,
    payload: EligibilityRulesUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_coordinator),
):
    rules = db.query(EligibilityRules).filter(
        EligibilityRules.opportunity_id == opportunity_id
    ).first()
    if not rules:
        raise HTTPException(status_code=404, detail="Eligibility rules not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rules, key, value)

    db.commit()
    db.refresh(rules)

    return {"message": "Eligibility rules updated", "eligibility": rules}


@eligibility_router.get("/{opportunity_id}/eligibility")
def get_eligibility_rules(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_coordinator),
):
    rules = db.query(EligibilityRules).filter(
        EligibilityRules.opportunity_id == opportunity_id
    ).first()
    if not rules:
        raise HTTPException(status_code=404, detail="Eligibility rules not found")

    return {"eligibility": rules}