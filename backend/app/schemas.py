from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from .models import CaseStatus, ConfidenceLevel, ReviewDecision

class CaseBase(BaseModel):
    hostname: str
    device_type: str
    issue_description: str
    topology_note: Optional[str] = None
    severity: Optional[str] = None
    expected_fault: Optional[str] = None
    osi_layer: Optional[str] = None
    concept_tag: Optional[str] = None
    show_outputs: Optional[dict] = None

class CaseCreate(CaseBase):
    pass

class Case(CaseBase):
    id: UUID
    status: CaseStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AIDiagnosisBase(BaseModel):
    root_cause: str
    osi_layer: str
    confidence: ConfidenceLevel
    evidence: Optional[List[str]] = None
    next_commands: Optional[List[str]] = None
    fix_steps: Optional[List[str]] = None

class AIDiagnosisCreate(AIDiagnosisBase):
    case_id: UUID

class AIDiagnosis(AIDiagnosisBase):
    id: UUID
    case_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewBase(BaseModel):
    reviewer_name: str
    decision: ReviewDecision
    feedback: Optional[str] = None
    edited_actions: Optional[dict] = None

class ReviewCreate(ReviewBase):
    diagnosis_id: UUID
    case_id: UUID

class Review(ReviewBase):
    id: UUID
    diagnosis_id: UUID
    case_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResponsibleAILogBase(BaseModel):
    ai_original_root_cause: str
    human_corrected_value: str
    correction_reason: str
    action_taken: str

class ResponsibleAILogCreate(ResponsibleAILogBase):
    case_id: UUID
    review_id: UUID

class ResponsibleAILog(ResponsibleAILogBase):
    id: UUID
    case_id: UUID
    review_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
