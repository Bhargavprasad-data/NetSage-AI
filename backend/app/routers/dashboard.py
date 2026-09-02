from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Total Cases
    total_cases = db.query(models.Case).count()
    
    # Cases by status
    status_counts = db.query(models.Case.status, func.count(models.Case.id)).group_by(models.Case.status).all()
    status_dict = {status.value: count for status, count in status_counts}
    
    # Agreement Metric: accepted / (accepted + edited + rejected)
    reviews = db.query(models.Review.decision, func.count(models.Review.id)).group_by(models.Review.decision).all()
    review_dict = {decision.value: count for decision, count in reviews}
    
    accepted = review_dict.get(models.ReviewDecision.ACCEPTED.value, 0)
    edited = review_dict.get(models.ReviewDecision.EDITED.value, 0)
    rejected = review_dict.get(models.ReviewDecision.REJECTED.value, 0)
    
    total_reviews = accepted + edited + rejected
    agreement_percent = (accepted / total_reviews * 100) if total_reviews > 0 else 0
    
    return {
        "total_cases": total_cases,
        "cases_by_status": status_dict,
        "reviews": review_dict,
        "agreement_percent": agreement_percent
    }
