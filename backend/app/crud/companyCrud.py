# app/crud/crud_company.py

from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from fastapi import HTTPException, status
from sqlalchemy import or_

from app.models.company import Company
from app.schemas.profileCompany import CompanyCreate, CompanyUpdate
from sqlalchemy.orm import Session

def search_companies(db: Session, search: str, skip: int = 0, limit: int = 10):
    return db.query(Company).filter(
        or_(
            Company.name.ilike(f"%{search}%"),
            Company.industry.ilike(f"%{search}%")
        )
    ).offset(skip).limit(limit).all()


def create_company(db: Session, company_in: CompanyCreate) -> Company:
    existing_company = db.query(Company).filter(Company.website_url == company_in.website_url).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company with this website already exists",
        )
    company = Company(id=str(uuid4()), **company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_company(db: Session, company_id: str) -> Company:
    try:
        company_uuid = UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid company ID format",
        )
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return company


def get_companies(db: Session, skip: int = 0, limit: int = 10) -> list[Company]:
    return db.query(Company).offset(skip).limit(limit).all()


def update_company(db: Session, company_id: str, company_in: CompanyUpdate) -> Company | None:
    company = get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company doesn't exist"
        )
    for field, value in company_in.dict(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: str) -> Company | None:
    company = get_company(db, company_id)
    if company:
        db.delete(company)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company doesn't exist"
        )
    return company
