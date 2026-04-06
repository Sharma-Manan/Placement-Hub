# # app/routers/wall_of_fame.py

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from uuid import UUID
# from typing import Optional

# from app.db.session import get_db
# from app.models.wall_of_fame import WallOfFame
# from app.models.placed_student import PlacedStudent
# from app.models.student import Student
# from app.schemas.wall_of_fame import WallOfFameCreate, WallOfFameOut, WallOfFameUpdate
# from app.core.dependencies import require_coordinator

# wall_of_fame_router = APIRouter(prefix="/wall-of-fame", tags=["Wall of Fame"])


# @wall_of_fame_router.post("/", status_code=201)
# def add_to_wall(
#     data: WallOfFameCreate,
#     db: Session = Depends(get_db),
#     current_user = Depends(require_coordinator),   # not commented out anymore
# ):
#     # check placed student exists
#     placed = db.query(PlacedStudent).filter(
#         PlacedStudent.id == data.placed_student_id
#     ).first()
#     if not placed:
#         raise HTTPException(status_code=404, detail="Placed student not found")

#     # check not already on wall
#     existing = db.query(WallOfFame).filter(
#         WallOfFame.placed_student_id == data.placed_student_id
#     ).first()
#     if existing:
#         raise HTTPException(status_code=409, detail="Already on Wall of Fame")

#     entry = WallOfFame(
#         placed_student_id=data.placed_student_id,
#         greeting=data.greeting,
#         added_by=current_user.id,
#     )
#     db.add(entry)
#     db.commit()
#     db.refresh(entry)
#     return entry


# @wall_of_fame_router.get("/")   # public — no auth
# def list_wall_of_fame(
#     skip: int = 0,
#     limit: int = 50,
#     db: Session = Depends(get_db),
# ):
#     results = (
#         db.query(WallOfFame, PlacedStudent, Student)
#         .join(PlacedStudent, WallOfFame.placed_student_id == PlacedStudent.id)
#         .join(Student, PlacedStudent.student_id == Student.id)
#         .order_by(WallOfFame.is_featured.desc(), WallOfFame.created_at.desc())
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )

#     return {
#         "total": db.query(WallOfFame).count(),
#         "entries": [
#             {
#                 "id": str(wof.id),
#                 "student_name": f"{st.first_name} {st.last_name}",
#                 "roll_no": st.roll_no,
#                 "photo_url": st.resume_url,   # use photo_url if you add it to Student
#                 "batch_year": st.graduation_year,
#                 "branch": st.department_id,
#                 "company_name": ps.company_name,
#                 "role": ps.role,
#                 "ctc_lpa": ps.ctc_lpa,
#                 "greeting": wof.greeting,
#                 "is_featured": wof.is_featured,
#                 "placed_at": ps.placed_at,
#             }
#             for wof, ps, st in results
#         ],
#     }


# @wall_of_fame_router.patch("/{entry_id}")
# def update_wall_entry(
#     entry_id: UUID,
#     payload: WallOfFameUpdate,
#     db: Session = Depends(get_db),
#     _= Depends(require_coordinator),
# ):
#     entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
#     if not entry:
#         raise HTTPException(status_code=404, detail="Entry not found")

#     for key, value in payload.model_dump(exclude_unset=True).items():
#         setattr(entry, key, value)

#     db.commit()
#     db.refresh(entry)
#     return entry


# @wall_of_fame_router.delete("/{entry_id}", status_code=204)
# def remove_from_wall(
#     entry_id: UUID,
#     db: Session = Depends(get_db),
#     _= Depends(require_coordinator),
# ):
#     entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
#     if not entry:
#         raise HTTPException(status_code=404, detail="Entry not found")

#     db.delete(entry)
#     db.commit()


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.models.wall_of_fame import WallOfFame
from app.models.student import Student
from app.schemas.wall_of_fame import WallOfFameEnhanced, WallOfFameCreate, WallOfFameUpdate
from app.core.dependencies import require_coordinator

wall_of_fame_router = APIRouter(prefix="/api/wall-of-fame", tags=["Wall of Fame"])


@wall_of_fame_router.get(
    "/",
    response_model=List[WallOfFameEnhanced],
    summary="List Wall of Fame",
    description="Returns all wall of fame entries with complete student details"
)
def list_wall_of_fame(
    skip: int = 0,
    limit: int = 100,
    featured_only: bool = False,
    db: Session = Depends(get_db),
):
    """
    Get all wall of fame entries with full student information.
    
    Query params:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - featured_only: If true, only return featured students
    """
    
    query = db.query(WallOfFame)
    
    if featured_only:
        query = query.filter(WallOfFame.is_featured == True)
    
    # Order by featured first, then by created date
    query = query.order_by(
        WallOfFame.is_featured.desc(),
        WallOfFame.created_at.desc()
    )
    
    wall_entries = query.offset(skip).limit(limit).all()
    
    # Enrich with student details
    result = []
    
    for entry in wall_entries:
        # Get student details
        student = db.query(Student).filter(
            Student.id == entry.placed_student_id
        ).first()
        
        if not student:
            # Skip if student not found (data integrity issue)
            continue
        
        # Build enhanced response
        enhanced_entry = {
            "id": str(entry.id),
            "greeting": entry.greeting,
            "is_featured": entry.is_featured if hasattr(entry, 'is_featured') else False,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
            
            # Student details
            "student_id": str(student.id),
            "student_name": f"{student.first_name} {student.last_name}",
            "student_photo_url": student.profile_photo_url,
            "roll_no": student.roll_no,
            "department_id": student.department_id,
            "graduation_year": student.graduation_year,
            "cgpa": student.cgpa,
            
            # Placement details (if you have these fields in Student model)
            "company_name": getattr(student, 'placed_company_name', None),
            "ctc_lpa": getattr(student, 'placed_ctc_lpa', None),
            "placed_at": getattr(student, 'placed_at', None),
            
            # LinkedIn/GitHub for contact
            "linkedin_url": student.linkedin_url,
            "github_url": student.github_url,
        }
        
        result.append(enhanced_entry)
    
    return result


@wall_of_fame_router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add to Wall of Fame",
    description="Add a placed student to the wall of fame"
)
def add_to_wall(
    payload: WallOfFameCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_coordinator),
):
    """
    Add a student to wall of fame.
    Only coordinators can do this.
    """
    
    # Verify student exists and is placed
    student = db.query(Student).filter(Student.id == payload.placed_student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.placement_status != "placed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student must be marked as 'placed' first"
        )
    
    # Check if already exists
    existing = db.query(WallOfFame).filter(
        WallOfFame.placed_student_id == payload.placed_student_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already in wall of fame"
        )
    
    # Create entry
    new_entry = WallOfFame(
        placed_student_id=payload.placed_student_id,
        greeting=payload.greeting,
        is_featured=getattr(payload, 'is_featured', False),
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    return {
        "id": str(new_entry.id),
        "message": "Student added to wall of fame successfully",
        "student_name": f"{student.first_name} {student.last_name}"
    }


@wall_of_fame_router.patch(
    "/{entry_id}",
    response_model=dict,
    summary="Update Wall Entry",
    description="Update greeting or featured status"
)
def update_wall_entry(
    entry_id: UUID,
    payload: WallOfFameUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_coordinator),
):
    """
    Update wall of fame entry.
    Only coordinators can do this.
    """
    
    entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wall of fame entry not found"
        )
    
    # Update fields
    if payload.greeting is not None:
        entry.greeting = payload.greeting
    
    if payload.is_featured is not None:
        entry.is_featured = payload.is_featured
    
    entry.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(entry)
    
    return {
        "id": str(entry.id),
        "message": "Wall of fame entry updated successfully"
    }


@wall_of_fame_router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove from Wall",
    description="Remove a student from wall of fame"
)
def remove_from_wall(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_coordinator),
):
    """
    Remove entry from wall of fame.
    Only coordinators can do this.
    """
    
    entry = db.query(WallOfFame).filter(WallOfFame.id == entry_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wall of fame entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return None