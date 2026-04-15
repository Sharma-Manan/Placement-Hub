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

    # 1. Find the company by name from the form.
    #    The name should be an exact match (case-insensitive).
    company = db.query(Company).filter(
        Company.name.ilike(opportunity_in.company_name)
    ).first()

    # 2. If the company doesn't exist, we must stop.
    #    The company profile (with logo and website) must be created first.
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{opportunity_in.company_name}' not found. Please create the company profile before adding an opportunity for it."
        )

    # 3. Create the new opportunity object, copying data from the found company.
    new_opportunity = Opportunity(
        # Fields from the form (title, description, etc.)
        title=opportunity_in.title,
        description=opportunity_in.description,
        location=opportunity_in.location,
        ctc_lpa=opportunity_in.ctc_lpa,
        application_deadline=opportunity_in.application_deadline,
        status=opportunity_in.status,
        additional_criteria=getattr(opportunity_in, 'additional_criteria', None),

        # The JD URL from the file upload
        jd_url=jd_url,

        # === THE FIX: Data is copied from the Company record ===
        company_id=company.id,
        company_name=company.name,      # Denormalized for performance
        company_logo=company.logo_url,    # Copied from Company table
        company_url=company.website_url,  # Copied from Company table
    )

    db.add(new_opportunity)
    db.commit()
    db.refresh(new_opportunity)

    return new_opportunity


# def create_opportunity(
#     db: Session,
#     opportunity_in: OpportunityCreate,
#     jd_url: str | None = None
# ) -> Opportunity:

#     # 1. Find company
#     company = db.query(Company).filter(
#         Company.name.ilike(opportunity_in.company_name)
#     ).first()

#     # 2. Create if not exists
#     if not company:
#         company = Company(name=opportunity_in.company_name)
#         db.add(company)
#         db.commit()
#         db.refresh(company)

#     # 3. Prepare data
#     data = opportunity_in.model_dump()
#     data["jd_url"] = jd_url

#     data.pop("company_name", None)

#     # 4. Create opportunity
#     opportunity = Opportunity(
#         **data,
#         company_id=company.id,
#         company_name=company.name
#     )

#     db.add(opportunity)
#     db.commit()
#     db.refresh(opportunity)

#     return opportunity

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
