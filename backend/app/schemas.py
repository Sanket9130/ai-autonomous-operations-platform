"""
Re-export schemas for unified access.
"""

from backend.app.schemas.asset import (
    AssetBase,
    AssetResponse,
    AssetDetailResponse,
    TelemetryResponse,
    MaintenanceResponse,
)
from backend.app.schemas.inventory import (
    InventoryBase,
    InventoryResponse,
    InventoryItemResponse,
)
from backend.app.schemas.technician import (
    TechnicianBase,
    TechnicianResponse,
)
from backend.app.schemas.operation import (
    OperationAsset,
    OperationPrediction,
    OperationInventory,
    OperationTechnician,
    OperationRoute,
    OperationSLA,
    OperationCost,
    OperationDecision,
    OperationResponse,
    TriggerOperationRequest,
    AutonomousOperationBackendResponse,
)
from backend.app.schemas.ai_engine import (
    AIEngineTelemetry,
    AIEngineMaintenance,
    AIEngineSparePart,
    AIEngineRequest,
    AIEngineResponse,
)

__all__ = [
    "AssetBase",
    "AssetResponse",
    "AssetDetailResponse",
    "TelemetryResponse",
    "MaintenanceResponse",
    "InventoryBase",
    "InventoryResponse",
    "InventoryItemResponse",
    "TechnicianBase",
    "TechnicianResponse",
    "OperationAsset",
    "OperationPrediction",
    "OperationInventory",
    "OperationTechnician",
    "OperationRoute",
    "OperationSLA",
    "OperationCost",
    "OperationDecision",
    "OperationResponse",
    "TriggerOperationRequest",
    "AutonomousOperationBackendResponse",
    "AIEngineTelemetry",
    "AIEngineMaintenance",
    "AIEngineSparePart",
    "AIEngineRequest",
    "AIEngineResponse",
]
