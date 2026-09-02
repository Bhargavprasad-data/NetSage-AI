import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from .database import Base

class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    DIAGNOSED = "DIAGNOSED"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"

class ConfidenceLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ReviewDecision(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"

class Case(Base):
    __tablename__ = "cases"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = Column(String, index=True)
    device_type = Column(String)
    issue_description = Column(Text)
    topology_note = Column(Text)
    severity = Column(String)
    expected_fault = Column(String)
    osi_layer = Column(String)
    concept_tag = Column(String)
    show_outputs = Column(JSON)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    diagnoses = relationship("AIDiagnosis", back_populates="case")
    reviews = relationship("Review", back_populates="case")
    ra_logs = relationship("ResponsibleAILog", back_populates="case")

class AIDiagnosis(Base):
    __tablename__ = "ai_diagnoses"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"))
    root_cause = Column(Text)
    osi_layer = Column(String)
    confidence = Column(Enum(ConfidenceLevel))
    evidence = Column(JSON)
    fix_steps = Column(JSON)
    next_commands = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="diagnoses")
    reviews = relationship("Review", back_populates="diagnosis")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagnosis_id = Column(Uuid(as_uuid=True), ForeignKey("ai_diagnoses.id"))
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"))
    reviewer_name = Column(String)
    decision = Column(Enum(ReviewDecision))
    feedback = Column(Text)
    edited_actions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="reviews")
    diagnosis = relationship("AIDiagnosis", back_populates="reviews")
    ra_logs = relationship("ResponsibleAILog", back_populates="review")

class ResponsibleAILog(Base):
    __tablename__ = "responsible_ai_log"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"))
    review_id = Column(Uuid(as_uuid=True), ForeignKey("reviews.id"))
    ai_original_root_cause = Column(Text)
    human_corrected_value = Column(Text)
    correction_reason = Column(Text)
    action_taken = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="ra_logs")
    review = relationship("Review", back_populates="ra_logs")
