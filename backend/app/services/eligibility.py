from sqlalchemy.orm import Session
from app.models.eligibility_rules import EligibilityRules


def check_eligibility(student, opportunity, db: Session):

    rules = db.query(EligibilityRules).filter(
        EligibilityRules.opportunity_id == opportunity.id
    ).first()

    # No rules → allow
    if not rules:
        return True

    # CGPA
    if rules.min_cgpa is not None:
        if student.cgpa < rules.min_cgpa:
            return False

    # Backlogs
    if rules.max_backlogs is not None:
        if student.active_backlogs > rules.max_backlogs:
            return False

    # Department
    if rules.allowed_depts:
        if student.department_id not in rules.allowed_depts:
            return False

    # Batch
    if rules.allowed_batches:
        if student.graduation_year not in rules.allowed_batches:
            return False

    # Prior offer
    if rules.no_prior_offer:
        if student.placement_status != "unplaced":
            return False

    return True