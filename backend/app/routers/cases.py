from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/cases",
    tags=["cases"]
)

@router.post("/", response_model=schemas.Case)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    return crud.create_case(db=db, case=case)

@router.get("/", response_model=List[schemas.Case])
def read_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cases = crud.get_cases(db, skip=skip, limit=limit)
    return cases

@router.get("/{case_id}", response_model=schemas.Case)
def read_case(case_id: UUID, db: Session = Depends(get_db)):
    db_case = crud.get_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case
