# app/crud/opportunity.py

from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status

from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.models.company import Company


def create_opportunity(
    db: Session,
    opportunity_in: OpportunityCreate,
    jd_url: str | None = None
) -> Opportunity:

    # 1. Find company
    company = db.query(Company).filter(
        Company.name.ilike(opportunity_in.company_name)
    ).first()

    # 2. Create if not exists
    if not company:
        company = Company(name=opportunity_in.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    # 3. Prepare data
    data = opportunity_in.model_dump()
    data["jd_url"] = jd_url

    data.pop("company_name", None)

    # 4. Create opportunity
    opportunity = Opportunity(
        **data,
        company_id=company.id,
        company_name=company.name
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return opportunity

def get_opportunity(db: Session, opportunity_id: UUID) -> Opportunity:
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == str(opportunity_id)
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    company = db.query(Company).filter(Company.id == opportunity.company_id).first()
    opportunity.company_name = company.name if company else None
    return opportunity


def get_opportunities(
    db:    Session,
    skip:  int = 0,
    limit: int = 10,
) -> list[Opportunity]:
    opportunities = (
    db.query(Opportunity)
    .order_by(Opportunity.created_at.desc())
    .offset(skip)
    .limit(limit)
    .all()
)

# 🔽 ADD THIS LOOP
    for op in opportunities:
        company = db.query(Company).filter(Company.id == op.company_id).first()
        op.company_name = company.name if company else None

    return opportunities


def get_opportunities_by_company(
    db:         Session,
    company_id: UUID,
    skip:       int = 0,
    limit:      int = 10,
) -> list[Opportunity]:
    return (
        db.query(Opportunity)
        .filter(Opportunity.company_id == company_id)
        .order_by(Opportunity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_opportunities(
    db:    Session,
    skip:  int = 0,
    limit: int = 10,
) -> list[Opportunity]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    return (
        db.query(Opportunity)
        .filter(
            Opportunity.status == "active",
            Opportunity.application_deadline > now,
        )
        .order_by(Opportunity.application_deadline.asc())  
        .offset(skip)
        .limit(limit)
        .all()
    )



def update_opportunity(
    db: Session,
    opportunity_id: UUID,
    opportunity_in: OpportunityUpdate,
) -> Opportunity:
    opportunity = get_opportunity(db, opportunity_id)

    data = opportunity_in.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)
    return opportunity



def delete_opportunity(db: Session, opportunity_id: UUID) -> None:
    opportunity = get_opportunity(db, opportunity_id)
    db.delete(opportunity)
    db.commit()
