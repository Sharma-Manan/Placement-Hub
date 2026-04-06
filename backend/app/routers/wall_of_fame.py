# app/routers/wall_of_fame.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.models.wall_of_fame import WallOfFame
from app.models.placed_student import PlacedStudent
from app.models.student import Student
from app.schemas.wall_of_fame import WallOfFameCreate, WallOfFameOut, WallOfFameUpdate
from app.core.dependencies import require_coordinator

wall_of_fame_router = APIRouter(prefix="/wall-of-fame", tags=["Wall of Fame"])


@wall_of_fame_router.post("/", status_code=201)
def add_to_wall(
    data: WallOfFameCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_coordinator),   # not commented out anymore
):
    # check placed student exists
    placed = db.query(PlacedStudent).filter(
        PlacedStudent.id == data.placed_student_id
    ).first()
    if not placed:
        raise HTTPException(status_code=404, detail="Placed student not found")

    # check not already on wall
    existing = db.query(WallOfFame).filter(
        WallOfFame.placed_student_id == data.placed_student_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already on Wall of Fame")

    entry = WallOfFame(
        placed_student_id=data.placed_student_id,
        greeting=data.greeting,
        added_by=current_user.id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@wall_of_fame_router.get("/")   # public — no auth
def list_wall_of_fame(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    results = (
        db.query(WallOfFame, PlacedStudent, Student)
        .join(PlacedStudent, WallOfFame.placed_student_id == PlacedStudent.id)
        .join(Student, PlacedStudent.student_id == Student.id)
        .order_by(WallOfFame.is_featured.desc(), WallOfFame.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": db.query(WallOfFame).count(),
        "entries": [
            {
                "id": str(wof.id),
                "student_name": f"{st.first_name} {st.last_name}",
                "roll_no": st.roll_no,
                "photo_url": st.resume_url,   # use photo_url if you add it to Student
                "batch_year": st.graduation_year,
                "branch": st.department_id,
                "company_name": ps.company_name,
                "role": ps.role,
                "ctc_lpa": ps.ctc_lpa,
                "greeting": wof.greeting,
                "is_featured": wof.is_featured,
                "placed_at": ps.placed_at,
            }
            for wof, ps, st in results
        ],
    }


@wall_of_fame_router.patch("/{entry_id}")
def update_wall_entry(
    entry_id: UUID,
    payload: WallOfFameUpdate,
    db: Session = Depends(get_db),
    _= Depends(require_coordinator),
):
    entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)

    db.commit()
    db.refresh(entry)
    return entry


@wall_of_fame_router.delete("/{entry_id}", status_code=204)
def remove_from_wall(
    entry_id: UUID,
    db: Session = Depends(get_db),
    _= Depends(require_coordinator),
):
    entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()