from backend.app.schemas.asset import (
    AssetBase,
    AssetResponse,
    AssetDetailResponse,
    TelemetryResponse,
    MaintenanceResponse,
)
from backend.app.schemas.inventory import InventoryBase, InventoryResponse
from backend.app.schemas.technician import TechnicianBase, TechnicianResponse
from backend.app.schemas.ai_engine import (
    AIEngineRequest,
    AIEngineResponse,
    AIEngineTelemetry,
    AIEngineMaintenance,
    AIEngineSparePart,
)
from backend.app.schemas.operation import (
    OperationResponse,
    OperationAsset,
    OperationPrediction,
    OperationInventory,
    OperationTechnician,
    OperationRoute,
    OperationSLA,
    OperationCost,
    OperationDecision,
)

__all__ = [
    "AssetBase",
    "AssetResponse",
    "AssetDetailResponse",
    "TelemetryResponse",
    "MaintenanceResponse",
    "InventoryBase",
    "InventoryResponse",
    "TechnicianBase",
    "TechnicianResponse",
    "AIEngineRequest",
    "AIEngineResponse",
    "AIEngineTelemetry",
    "AIEngineMaintenance",
    "AIEngineSparePart",
    "OperationResponse",
    "OperationAsset",
    "OperationPrediction",
    "OperationInventory",
    "OperationTechnician",
    "OperationRoute",
    "OperationSLA",
    "OperationCost",
    "OperationDecision",
]
