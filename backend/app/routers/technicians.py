"""
Technicians Router.
Provides endpoints to query certified technicians and current shift availability.
"""

from typing import Any, Dict, List
from fastapi import APIRouter
from backend.app.database import get_candidate_technicians

router = APIRouter(prefix="/api/technicians", tags=["Technicians"])


@router.get("", summary="List available technicians")
async def list_technicians():
    """List all available field technicians."""
    return get_candidate_technicians(only_available=False)
