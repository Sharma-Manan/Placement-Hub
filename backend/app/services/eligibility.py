from sqlalchemy.orm import Session
from app.models.eligibility_rules import EligibilityRules

def check_eligibility(student, opportunity, db: Session):

    rules = db.query(EligibilityRules).filter(
        EligibilityRules.opportunity_id == opportunity.id
    ).first()

    
    if not rules:
        return True, None

    
    if rules.min_cgpa is not None:
        if student.cgpa < rules.min_cgpa:
            return False, f"Requires CGPA >= {rules.min_cgpa} (you have {student.cgpa})"

    
    if rules.max_backlogs is not None:
        if student.active_backlogs > rules.max_backlogs:
            return False, f"Max {rules.max_backlogs} backlogs allowed (you have {student.active_backlogs})"

    
    if rules.allowed_depts:
        if student.department_id not in rules.allowed_depts:
            return False, "Your department is not eligible"

    
    if rules.allowed_batches:
        if student.graduation_year not in rules.allowed_batches:
            return False, f"Only batches {rules.allowed_batches} allowed"

    
    if rules.no_prior_offer:
        if student.placement_status != "unplaced":
            return False, "Students with prior offers are not allowed"

    return True, None