from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

@router.post("/", response_model=schemas.Review)
def submit_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    case = crud.get_case(db, review.case_id)
    diagnosis = crud.get_diagnosis_by_case(db, review.case_id)

    if not case or not diagnosis:
        raise HTTPException(status_code=404, detail="Case or Diagnosis not found")
    
    if diagnosis.id != review.diagnosis_id:
        raise HTTPException(status_code=400, detail="Diagnosis ID mismatch")

    # Create the review
    db_review = crud.create_review(db, review)
    
    # Update Case status to REVIEWED
    crud.update_case_status(db, review.case_id, models.CaseStatus.REVIEWED)

    # Automatic Responsible AI Logging
    if review.decision in [models.ReviewDecision.EDITED, models.ReviewDecision.REJECTED]:
        # Formulate human corrected value and reason from feedback or edited actions
        human_corrected = str(review.edited_actions) if review.edited_actions else review.feedback or "Rejected/Edited without specific correction text."
        
        ra_log = schemas.ResponsibleAILogCreate(
            case_id=review.case_id,
            review_id=db_review.id,
            ai_original_root_cause=diagnosis.root_cause,
            human_corrected_value=human_corrected,
            correction_reason=review.feedback or "Reviewer deemed AI diagnosis incorrect or incomplete.",
            action_taken=review.decision.value
        )
        crud.create_ra_log(db, ra_log)

    return db_review
