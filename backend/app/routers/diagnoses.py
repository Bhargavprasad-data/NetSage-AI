from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud, models, schemas
from ..database import get_db
from ..llm import generate_diagnosis_prompt, mock_llm_inference
from ..rules import run_all_rules
from ..verifier import verify_evidence

router = APIRouter(
    prefix="/diagnoses",
    tags=["diagnoses"]
)

@router.post("/case/{case_id}", response_model=schemas.AIDiagnosis)
def orchestrate_diagnosis(case_id: UUID, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case.status not in [models.CaseStatus.OPEN]:
        raise HTTPException(status_code=400, detail="Case is already diagnosed or resolved")

    # Step 1: Deterministic rules
    rule_evidence = run_all_rules(case.show_outputs or {})

    # Step 2: Formulate prompt
    prompt = generate_diagnosis_prompt(case)

    # Step 3: LLM Inference
    llm_output = mock_llm_inference(prompt, rule_evidence, case)

    # Step 4: Verify evidence (this is usually done on read, but we can verify initially too)
    # The prompt explicitly asks to "recompute on read" for the human reviewer.
    # So we'll just save what the LLM gave us.
    
    diagnosis_create = schemas.AIDiagnosisCreate(
        case_id=case_id,
        root_cause=llm_output.root_cause,
        osi_layer=llm_output.osi_layer,
        confidence=llm_output.confidence,
        evidence=llm_output.evidence,
        fix_steps=llm_output.fix_steps,
        next_commands=llm_output.next_commands
    )

    diagnosis = crud.create_diagnosis(db, diagnosis_create)
    crud.update_case_status(db, case_id, models.CaseStatus.DIAGNOSED)
    
    return diagnosis

@router.get("/case/{case_id}")
def get_diagnosis_for_case(case_id: UUID, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    diagnosis = crud.get_diagnosis_by_case(db, case_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    # Dynamic Evidence Verification on read
    verification_results = verify_evidence(diagnosis.evidence, case.show_outputs or {})
    
    # Return enriched response
    return {
        "diagnosis": schemas.AIDiagnosis.model_validate(diagnosis),
        "verification_results": verification_results
    }
