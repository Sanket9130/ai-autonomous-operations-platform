from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.technician import Technician
from backend.app.schemas.technician import TechnicianResponse

router = APIRouter(prefix="/api/technicians", tags=["Technicians"])


@router.get("", response_model=List[TechnicianResponse])
def get_technicians(
    available_only: Optional[bool] = Query(None, description="Filter by availability status"),
    db: Session = Depends(get_db)
):
    """
    Retrieve technicians. Database-driven, no hardcoded records in application logic.
    Supports optional filtering by availability.
    """
    query = db.query(Technician)
    if available_only is not None:
        query = query.filter(Technician.availability == available_only)
    technicians = query.all()
    return technicians


@router.get("/{technician_id}", response_model=TechnicianResponse)
def get_technician(technician_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific technician by technician_id.
    """
    tech = db.query(Technician).filter(Technician.technician_id == technician_id).first()
    if not tech:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician '{technician_id}' not found."
        )
    return tech
