from fastapi import APIRouter
from backend.app.api.assets import router as assets_router
from backend.app.api.inventory import router as inventory_router
from backend.app.api.technicians import router as technicians_router
from backend.app.api.operations import router as operations_router

api_router = APIRouter()
api_router.include_router(assets_router)
api_router.include_router(inventory_router)
api_router.include_router(technicians_router)
api_router.include_router(operations_router)

__all__ = ["api_router"]
