from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.announcement import Announcement
from app.models.student import Student
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut, MentionedStudent
from app.core.dependencies import require_coordinator
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.services.notification_service import notify_students_bulk, notify_student
from app.models.notification import NotificationType

announcement_router = APIRouter(prefix="/announcements", tags=["Announcements"])


def resolve_mentions(message: str, mentioned_students: list) -> str:
    """
    Replace @student:<uuid> tokens in message with actual student names.
    Input:  "@student:abc-uuid has been placed at Google!"
    Output: "@Rahul Sharma has been placed at Google!"
    """
    display = message
    for student, user in mentioned_students:
        token = f"@student:{str(student.id)}"
        name = f"@{student.first_name} {student.last_name}"
        display = display.replace(token, name)
    return display


# ─────────────────────────────────────────────────
# POST /announcements  (Coordinator only)
# ─────────────────────────────────────────────────
@announcement_router.post(
    "/",
    response_model=AnnouncementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Announcement",
    description="Coordinator posts an announcement. Use @student:<uuid> in message to mention students."
)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    # 1. Resolve mentioned students
    mentioned_students = []  # list of (Student, User) tuples
    if payload.mentioned_student_ids:
        for sid in payload.mentioned_student_ids:
            student = db.query(Student).filter(Student.id == sid).first()
            if not student:
                raise HTTPException(
                    status_code=404,
                    detail=f"Mentioned student {sid} not found"
                )
            user = db.query(User).filter(User.id == student.user_id).first()
            mentioned_students.append((student, user))

    # 2. Build display_message (resolve @student:<uuid> → @Name)
    display_msg = resolve_mentions(payload.message, mentioned_students)

    # 3. Create announcement
    announcement = Announcement(
        coordinator_id=current_user.id,
        title=payload.title,
        message=payload.message,
        display_message=display_msg,
        announcement_type=payload.announcement_type,
        related_opportunity_id=payload.related_opportunity_id,
        mentioned_student_ids=[s.id for s, _ in mentioned_students] if mentioned_students else None,
        is_pinned=payload.is_pinned or False,
    )

    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    # 4. Get coordinator name for response
    coordinator = db.query(User).filter(User.id == current_user.id).first()
    coordinator_name = f"{coordinator.first_name} {coordinator.last_name}" if coordinator else "Coordinator"

    # ── NOTIFICATIONS ──────────────────────────────────────────

    # 4a. Notify ALL students about the announcement
    all_students = db.query(Student).all()
    all_user_ids = [s.user_id for s in all_students]

    if all_user_ids:
        from app.models.notification import Notification

        notifs = [
            Notification(
                user_id=uid,
                role="student",
                type=NotificationType.NEW_OPPORTUNITY
                    if payload.announcement_type == "placement"
                    else NotificationType.DEADLINE_REMINDER,
                title=payload.title,
                message=display_msg[:200],  # truncate for notification
                related_opportunity_id=payload.related_opportunity_id,
            )
            for uid in all_user_ids
        ]
        db.bulk_save_objects(notifs)
        db.commit()

    # 4b. Extra personal notification for each @mentioned student
    for student, user in mentioned_students:
        notify_student(
            db=db,
            user_id=student.user_id,
            type=NotificationType.WALL_OF_FAME_ADDED,  # reuse or add new type
            title=f"You were mentioned in: {payload.title}",
            message=display_msg,
            related_opportunity_id=payload.related_opportunity_id,
        )

    # 5. Build response
    return _build_response(announcement, mentioned_students, coordinator_name)


# ─────────────────────────────────────────────────
# GET /announcements  (Students + Coordinators)
# ─────────────────────────────────────────────────
@announcement_router.get(
    "/",
    response_model=List[AnnouncementOut],
    summary="List Announcements",
    description="All users can view announcements. Pinned ones appear first."
)
def list_announcements(
    skip: int = 0,
    limit: int = 50,
    announcement_type: Optional[str] = Query(None, description="Filter by type"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    query = db.query(Announcement)

    if announcement_type:
        query = query.filter(Announcement.announcement_type == announcement_type)

    announcements = query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for ann in announcements:
        coordinator = db.query(User).filter(User.id == ann.coordinator_id).first()
        coordinator_name = f"{coordinator.first_name} {coordinator.last_name}" if coordinator else "Coordinator"

        mentioned = _fetch_mentioned_students(db, ann.mentioned_student_ids)
        result.append(_build_response(ann, mentioned, coordinator_name))

    return result


# ─────────────────────────────────────────────────
# GET /announcements/{id}
# ─────────────────────────────────────────────────
@announcement_router.get(
    "/{announcement_id}",
    response_model=AnnouncementOut,
    summary="Get Single Announcement"
)
def get_announcement(
    announcement_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    coordinator = db.query(User).filter(User.id == ann.coordinator_id).first()
    coordinator_name = f"{coordinator.first_name} {coordinator.last_name}" if coordinator else "Coordinator"
    mentioned = _fetch_mentioned_students(db, ann.mentioned_student_ids)

    return _build_response(ann, mentioned, coordinator_name)


# ─────────────────────────────────────────────────
# PATCH /announcements/{id}  (Coordinator only)
# ─────────────────────────────────────────────────
@announcement_router.patch(
    "/{announcement_id}",
    response_model=AnnouncementOut,
    summary="Update Announcement"
)
def update_announcement(
    announcement_id: UUID,
    payload: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if payload.title is not None:
        ann.title = payload.title
    if payload.message is not None:
        ann.message = payload.message
        # Re-resolve display message
        mentioned = _fetch_mentioned_students(db, ann.mentioned_student_ids)
        ann.display_message = resolve_mentions(payload.message, mentioned)
    if payload.is_pinned is not None:
        ann.is_pinned = payload.is_pinned

    db.commit()
    db.refresh(ann)

    coordinator = db.query(User).filter(User.id == ann.coordinator_id).first()
    coordinator_name = f"{coordinator.first_name} {coordinator.last_name}" if coordinator else "Coordinator"
    mentioned = _fetch_mentioned_students(db, ann.mentioned_student_ids)

    return _build_response(ann, mentioned, coordinator_name)


# ─────────────────────────────────────────────────
# DELETE /announcements/{id}  (Coordinator only)
# ─────────────────────────────────────────────────
@announcement_router.delete(
    "/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Announcement"
)
def delete_announcement(
    announcement_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    db.delete(ann)
    db.commit()
    return None


# ─────────────────────────────────────────────────
# GET /announcements/students/search  (Coordinator helper)
# For the @mention autocomplete in frontend
# ─────────────────────────────────────────────────
@announcement_router.get(
    "/students/search",
    summary="Search Students for @mention",
    description="Coordinator uses this to search students by name or roll_no for @mention autocomplete"
)
def search_students_for_mention(
    q: str = Query(..., min_length=1, description="Search by name or roll_no"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_coordinator),
):
    students = db.query(Student).filter(
        (Student.first_name.ilike(f"%{q}%")) |
        (Student.last_name.ilike(f"%{q}%")) |
        (Student.roll_no.ilike(f"%{q}%"))
    ).limit(10).all()

    return [
        {
            "student_id": str(s.id),
            "name": f"{s.first_name} {s.last_name}",
            "roll_no": s.roll_no,
            "department_id": s.department_id,
            "placement_status": s.placement_status,
            # token to embed in message
            "mention_token": f"@student:{str(s.id)}"
        }
        for s in students
    ]


# ─────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────
def _fetch_mentioned_students(db: Session, mentioned_ids):
    """Fetch (Student, User) tuples for a list of student ids."""
    if not mentioned_ids:
        return []
    result = []
    for sid in mentioned_ids:
        student = db.query(Student).filter(Student.id == sid).first()
        if student:
            user = db.query(User).filter(User.id == student.user_id).first()
            result.append((student, user))
    return result


def _build_response(announcement: Announcement, mentioned_students: list, coordinator_name: str) -> dict:
    """Build the AnnouncementOut dict."""
    mentioned_out = [
        MentionedStudent(
            student_id=s.id,
            student_name=f"{s.first_name} {s.last_name}",
            roll_no=s.roll_no,
        )
        for s, _ in mentioned_students
    ]

    return AnnouncementOut(
        id=announcement.id,
        title=announcement.title,
        message=announcement.message,
        display_message=announcement.display_message or announcement.message,
        announcement_type=announcement.announcement_type,
        related_opportunity_id=announcement.related_opportunity_id,
        mentioned_students=mentioned_out if mentioned_out else None,
        is_pinned=announcement.is_featured if hasattr(announcement, 'is_featured') else announcement.is_pinned,
        coordinator_name=coordinator_name,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
    )