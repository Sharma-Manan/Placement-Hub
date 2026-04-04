# app/crud/wall_of_fame.py

from uuid import UUID
from sqlalchemy.orm import Session

from app.models.wall_of_fame import WallOfFame
from app.models.student import Student
from app.schemas.wall_of_fame import WallOfFameCreate


def add_to_wall_of_fame(
    db: Session,
    data: WallOfFameCreate,
    added_by: UUID,
) -> WallOfFame:
    # verify student exists and is placed
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise ValueError("Student not found")
    if student.placement_status != "placed":
        raise ValueError("Student is not placed yet")

    # check duplicate
    exists = (
        db.query(WallOfFame)
        .filter(WallOfFame.student_id == data.student_id)
        .first()
    )
    if exists:
        raise ValueError("Student already on Wall of Fame")

    entry = WallOfFame(**data.model_dump(), added_by=added_by)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_wall_of_fame(
    db: Session,
    batch_year: int | None = None,
    skip: int = 0,
    limit: int = 50,
):
    query = (
        db.query(
            WallOfFame,
            Student.first_name,
            Student.last_name,
            Student.department_id,
        )
        .join(Student, WallOfFame.student_id == Student.id)
    )
    if batch_year:
        query = query.filter(WallOfFame.batch_year == batch_year)

    return query.order_by(WallOfFame.created_at.desc()).offset(skip).limit(limit).all()


def remove_from_wall_of_fame(db: Session, entry_id: UUID) -> bool:
    entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True