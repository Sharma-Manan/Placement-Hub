from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_coordinator

from app.models.placed_student import PlacedStudent
from app.models.student import Student
from app.models.wall_of_fame import WallOfFame

router = APIRouter(tags=["Placed Students"])
@router.get("/placed/search")
def search_placed_students(
    roll: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    _ = Depends(require_coordinator),
):
    results = (
        db.query(PlacedStudent, Student)
        .join(Student, PlacedStudent.student_id == Student.id)
        .filter(Student.roll_no.ilike(f"%{roll}%"))
        .all()
    )

    return [
        {
            "placed_student_id": str(ps.id),
            "roll_no": st.roll_no,
            "student_name": f"{st.first_name} {st.last_name}",
            "photo_url": None,           # add photo_url to Student model if needed
            "batch_year": st.graduation_year,
            "branch": st.department_id,
            "company_name": ps.company_name,
            "role": ps.role,
            "ctc_lpa": ps.ctc_lpa,
            "already_on_wall": db.query(WallOfFame)
                .filter_by(placed_student_id=ps.id).first() is not None,
        }
        for ps, st in results
    ]