from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import Event, EventStudent
from app.schemas.event import EventCreate, EventResponse
from typing import List
from uuid import UUID
from app.models.application import Application
from fastapi import HTTPException
from app.models.opportunity import Opportunity

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):

    # Validate opportunity
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == payload.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")


    # Validate event type
    if payload.event_type not in ["test", "interview"]:
        raise HTTPException(status_code=400, detail="Invalid event type")

    # 1. Create Event
    new_event = Event(
        opportunity_id=payload.opportunity_id,
        event_type=payload.event_type,
        title=payload.title,
        description=payload.description,
        event_datetime=payload.event_datetime,
        duration_minutes=payload.duration_minutes,
        location=payload.location
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # 2. Assign Students (if provided)
    if payload.student_ids:
        student_ids = list(set(payload.student_ids))
    else:
        student_ids = list(set([
            app.student_id
            for app in db.query(Application).filter(
                Application.opportunity_id == payload.opportunity_id,
                Application.status == "shortlisted"
            ).all()
        ]))

    if student_ids:
        event_students = [
            EventStudent(
                event_id=new_event.id,  
                student_id=student_id
            )
            for student_id in student_ids
        ]

        db.bulk_save_objects(event_students)
        db.commit()

    return new_event

@router.get("/{opportunity_id}", response_model=List[EventResponse])
def get_events_by_opportunity(opportunity_id: UUID, db: Session = Depends(get_db)):

    events = db.query(Event).filter(
        Event.opportunity_id == opportunity_id
    ).order_by(Event.event_datetime).all()

    return events