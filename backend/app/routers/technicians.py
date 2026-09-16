"""
Technicians Router.
Provides endpoints to query certified technicians and current shift availability.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.technician import Technician
from backend.app.schemas.technician import TechnicianResponse

router = APIRouter(prefix="/api/technicians", tags=["Technicians"])


@router.get("", response_model=List[TechnicianResponse], summary="List available technicians")
async def list_technicians(
    available_only: Optional[bool] = Query(default=None, description="Filter by availability"),
    db: Session = Depends(get_db),
):
    """List field technicians with optional availability filter."""
    query = db.query(Technician)
    if available_only is True:
        query = query.filter(Technician.availability.is_(True))
    elif available_only is False:
        query = query.filter(Technician.availability.is_(False))

    technicians = query.order_by(Technician.technician_id.asc()).all()
    return technicians


@router.get("/{technician_id}", response_model=TechnicianResponse, summary="Get technician by ID")
async def get_technician(technician_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific technician by ID."""
    technician = db.query(Technician).filter(Technician.technician_id == technician_id).first()
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technician '{technician_id}' not found.",
        )
    return technician
