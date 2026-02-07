from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from app.models.company import Company 
from app.schemas.profileCompany import CompanyCreate, CompanyOut, CompanyUpdate
from app.crud.companyCrud import (
    create_company,
    get_company,
    get_companies,
    update_company,
    delete_company,
    search_companies
)
from app.db.session import get_db

company_router = APIRouter(prefix="/companies", tags=["Companies"])

@company_router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED,)
def create_company_endpoint(company: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, company)

@company_router.get("/{company_id}", response_model=CompanyOut)
def read_company_endpoint(company_id: str, db: Session = Depends(get_db)):
    return get_company(db, company_id)

@company_router.get("/", response_model=List[CompanyOut])
def list_companies_endpoint(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Search by name or industry"),
    db: Session = Depends(get_db)
):
    if search:
        return search_companies(db, search=search, skip=skip, limit=limit)
    return get_companies(db, skip=skip, limit=limit)

@company_router.put("/{company_id}", response_model=CompanyOut)
def update_company_endpoint(company_id: str, company_in: CompanyUpdate, db: Session = Depends(get_db)):
    return update_company(db, company_id, company_in)

@company_router.delete("/{company_id}", response_model=CompanyOut)
def delete_company_endpoint(company_id: str, db: Session = Depends(get_db)):
    return delete_company(db, company_id)
