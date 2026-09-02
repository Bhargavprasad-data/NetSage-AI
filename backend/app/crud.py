from sqlalchemy.orm import Session
from uuid import UUID
from . import models, schemas

def get_case(db: Session, case_id: UUID):
    return db.query(models.Case).filter(models.Case.id == case_id).first()

def get_cases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Case).offset(skip).limit(limit).all()

def create_case(db: Session, case: schemas.CaseCreate):
    db_case = models.Case(
        hostname=case.hostname,
        device_type=case.device_type,
        issue_description=case.issue_description,
        topology_note=case.topology_note,
        severity=case.severity,
        expected_fault=case.expected_fault,
        osi_layer=case.osi_layer,
        concept_tag=case.concept_tag,
        show_outputs=case.show_outputs
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def update_case_status(db: Session, case_id: UUID, status: models.CaseStatus):
    db_case = get_case(db, case_id)
    if db_case:
        db_case.status = status
        db.commit()
        db.refresh(db_case)
    return db_case

def create_diagnosis(db: Session, diagnosis: schemas.AIDiagnosisCreate):
    db_diagnosis = models.AIDiagnosis(
        case_id=diagnosis.case_id,
        root_cause=diagnosis.root_cause,
        osi_layer=diagnosis.osi_layer,
        confidence=diagnosis.confidence,
        evidence=diagnosis.evidence,
        fix_steps=diagnosis.fix_steps,
        next_commands=diagnosis.next_commands
    )
    db.add(db_diagnosis)
    db.commit()
    db.refresh(db_diagnosis)
    return db_diagnosis

def get_diagnosis_by_case(db: Session, case_id: UUID):
    return db.query(models.AIDiagnosis).filter(models.AIDiagnosis.case_id == case_id).first()

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(
        diagnosis_id=review.diagnosis_id,
        case_id=review.case_id,
        reviewer_name=review.reviewer_name,
        decision=review.decision,
        feedback=review.feedback,
        edited_actions=review.edited_actions
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def create_ra_log(db: Session, ra_log: schemas.ResponsibleAILogCreate):
    db_ra_log = models.ResponsibleAILog(
        case_id=ra_log.case_id,
        review_id=ra_log.review_id,
        ai_original_root_cause=ra_log.ai_original_root_cause,
        human_corrected_value=ra_log.human_corrected_value,
        correction_reason=ra_log.correction_reason,
        action_taken=ra_log.action_taken
    )
    db.add(db_ra_log)
    db.commit()
    db.refresh(db_ra_log)
    return db_ra_log
