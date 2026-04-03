from datetime import timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.event import Event, EventStudent


def detect_conflicts(events: List) -> List[Tuple]:
    """
    Detect overlapping events for a student.

    Args:
        events: List of event objects (must have event_datetime, duration_minutes)

    Returns:
        List of tuples: [(event1, event2), ...]
    """

    conflicts = []

    # Sort events by start time (optional optimization)
    events = sorted(events, key=lambda e: e.event_datetime)

    for i in range(len(events)):
        for j in range(i + 1, len(events)):

            event1 = events[i]
            event2 = events[j]

            start1 = event1.event_datetime
            end1 = start1 + timedelta(minutes=event1.duration_minutes)

            start2 = event2.event_datetime
            end2 = start2 + timedelta(minutes=event2.duration_minutes)

            # Overlap condition
            if start1 < end2 and start2 < end1:
                conflicts.append((event1, event2))

    return conflicts

#get events for a student
def get_student_events(db: Session, student_id):
    """
    Fetch all events assigned to a student
    """

    events = (
        db.query(Event)
        .join(EventStudent, Event.id == EventStudent.event_id)
        .filter(EventStudent.student_id == student_id)
        .all()
    )

    return events

def get_student_conflicts(db: Session, student_id):
    """
    Get all conflicting events for a student
    """

    # Step 1: Fetch events
    events = get_student_events(db, student_id)

    # Step 2: Detect conflicts
    conflicts = detect_conflicts(events)

    return conflicts