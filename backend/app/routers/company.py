from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.core.dependencies import require_coordinator


company_router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(require_coordinator)],
)


@company_router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db),
):
    data = payload.model_dump()

    for field in ["website_url", "logo_url"]:
        if data.get(field):
            data[field] = str(data[field])

    company = Company(**data)

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@company_router.get("/", response_model=list[CompanyOut])
def list_companies(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies


@company_router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@company_router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    data = payload.model_dump(exclude_unset=True)

    for field in ["website_url", "logo_url"]:
        if data.get(field):
            data[field] = str(data[field])

    for key, value in data.items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)

    return company


@company_router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()