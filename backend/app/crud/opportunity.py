from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from fastapi import HTTPException, status

from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate


def create_opportunity(db: Session, opportunity_in: OpportunityCreate) -> Opportunity:
    opportunity = Opportunity(
        **opportunity_in.model_dump()
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return opportunity


def get_opportunity(db: Session, opportunity_id: str) -> Opportunity:
    try:
        UUID(opportunity_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid opportunity ID format",
        )

    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    return opportunity


def get_opportunities(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Opportunity).offset(skip).limit(limit).all()


def update_opportunity(
    db: Session,
    opportunity_id: str,
    opportunity_in: OpportunityUpdate
) -> Opportunity:

    opportunity = get_opportunity(db, opportunity_id)

    for field, value in opportunity_in.model_dump(exclude_unset=True).items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)

    return opportunity


def delete_opportunity(db: Session, opportunity_id: str) -> Opportunity:

    opportunity = get_opportunity(db, opportunity_id)

    db.delete(opportunity)
    db.commit()

    return None