import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/csv",
    tags=["csv"]
)

@router.get("/export")
def export_cases(db: Session = Depends(get_db)):
    cases = crud.get_cases(db, skip=0, limit=10000)
    
    # Exclude raw show_outputs based on plan
    fieldnames = [
        "id", "hostname", "device_type", "issue_description", 
        "topology_note", "severity", "expected_fault", 
        "osi_layer", "concept_tag", "status", "created_at"
    ]
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for case in cases:
        writer.writerow({
            "id": str(case.id),
            "hostname": case.hostname,
            "device_type": case.device_type,
            "issue_description": case.issue_description,
            "topology_note": case.topology_note,
            "severity": case.severity,
            "expected_fault": case.expected_fault,
            "osi_layer": case.osi_layer,
            "concept_tag": case.concept_tag,
            "status": case.status.value,
            "created_at": case.created_at.isoformat()
        })
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=netsage_cases.csv"}
    )

@router.post("/import")
async def import_cases(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV allowed.")
    
    content = await file.read()
    decoded = content.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded))
    
    imported_count = 0
    for row in csv_reader:
        case_create = schemas.CaseCreate(
            hostname=row.get("hostname", ""),
            device_type=row.get("device_type", ""),
            issue_description=row.get("issue_description", ""),
            topology_note=row.get("topology_note"),
            severity=row.get("severity"),
            expected_fault=row.get("expected_fault"),
            osi_layer=row.get("osi_layer"),
            concept_tag=row.get("concept_tag"),
            show_outputs=None  # intentionally skipped in main CSV per plan
        )
        crud.create_case(db, case_create)
        imported_count += 1
        
    return {"message": f"Successfully imported {imported_count} cases."}
