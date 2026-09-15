"""
FastAPI Server for AI Autonomous Operations Intelligence Platform.

Primary Endpoint:
  POST /autonomous-operation (and POST /api/v1/autonomous-operation)

Sub-Endpoints:
  GET  /health
  POST /predict
  POST /forecast-demand
  POST /operations-decision
  POST /dispatch-technician
  POST /optimize-operation
"""

import os
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

from api.schemas import (
    AssetFailurePredictionResponse,
    AssetTelemetryInput,
    AutonomousOperationInput,
    AutonomousOperationResponse,
    DecisionIntelligenceInput,
    DecisionIntelligenceResponse,
    DemandForecastInput,
    DemandForecastResponse,
    HealthResponse,
    OptimizeOperationInput,
    OptimizeOperationResponse,
    TechnicianDispatchInput,
    TechnicianDispatchResponse,
    UnifiedOperationsDecisionInput,
    UnifiedOperationsDecisionResponse,
)
from src.forecasting.demand_forecast import forecast_spare_part_demand
from src.models.model_utils import load_metadata, load_model
from src.models.predict import predict_asset_failure
from src.recommendations.recommendation_engine import (
    evaluate_decision_intelligence,
    evaluate_unified_operations_decision,
    execute_autonomous_operations_pipeline,
)
from src.recommendations.technician_router import select_best_technician
from src.risk_engine.cost_optimizer import optimize_operational_decision

app = FastAPI(
    title="AI Autonomous Operations Intelligence API",
    description="Facility & Property Operations Decision Intelligence Engine (Dubai FM)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------
# Dynamic Environment-Configurable CORS Configuration
# ---------------------------------------------------------
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://localhost:5000,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8000,http://127.0.0.1:5000",
)

if cors_origins_env.strip() == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """Handle model unavailability or missing artifact errors gracefully."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "error_type": "ModelArtifactUnavailable"},
    )


# ---------------------------------------------------------
# Health & Status Endpoint
# ---------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Service health and model artifact readiness check."""
    model = load_model()
    metadata = load_metadata()
    return HealthResponse(
        status="healthy",
        service="ai-engine",
        version="1.0.0",
        model_loaded=(model is not None),
        selected_model=metadata.get("selected_model"),
    )


# ---------------------------------------------------------
# Primary Integration Endpoint: End-to-End Autonomous Operation
# ---------------------------------------------------------
@app.post(
    "/autonomous-operation",
    response_model=AutonomousOperationResponse,
    summary="Primary End-to-End Autonomous Operations Pipeline",
    tags=["Primary Autonomous Pipeline"],
)
@app.post(
    "/api/v1/autonomous-operation",
    response_model=AutonomousOperationResponse,
    summary="Primary End-to-End Autonomous Operations Pipeline (v1)",
    tags=["Primary Autonomous Pipeline"],
)
async def run_autonomous_operation(payload: AutonomousOperationInput) -> AutonomousOperationResponse:
    """
    Primary Autonomous Operations Endpoint.

    Connects:
      Telemetry -> ML Failure Prediction -> Asset Risk -> Spare-Part Demand Forecast
      -> Inventory Stockout Risk -> Technician Selection & Routing -> SLA Assessment
      -> Financial Cost Optimization -> Unified Operational Action.
    """
    telemetry = {
        "vibration_mm_s": payload.vibration_mm_s,
        "operating_temp_c": payload.operating_temp_c,
        "ambient_temp_c": payload.ambient_temp_c,
        "power_kw": payload.power_kw,
        "runtime_hours": payload.runtime_hours,
        "last_maintenance_days": payload.last_maintenance_days,
    }

    historical_demand = payload.historical_daily_demand
    if not historical_demand:
        data_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "spare_parts_demand.csv"
        if data_path.exists():
            try:
                df = pd.read_csv(data_path)
                subset = df[df["part_id"] == payload.required_spare_part]
                if not subset.empty:
                    historical_demand = subset["daily_demand"].tolist()
            except Exception:
                pass

    pipeline_result = execute_autonomous_operations_pipeline(
        asset_id=payload.asset_id,
        telemetry_features=telemetry,
        asset_type=payload.asset_type,
        asset_location=payload.asset_location,
        asset_criticality=payload.asset_criticality,
        required_spare_part=payload.required_spare_part,
        current_stock=payload.current_stock,
        lead_time_days=payload.lead_time_days,
        forecast_days=payload.forecast_days,
        spare_part_cost=payload.spare_part_cost,
        sla_deadline_hours=payload.sla_deadline_hours,
        estimated_repair_duration_hours=payload.estimated_repair_duration_hours,
        candidate_technicians=payload.candidate_technicians,
        historical_daily_demand=historical_demand,
    )
    return AutonomousOperationResponse(**pipeline_result)


# ---------------------------------------------------------
# Sub-Endpoints
# ---------------------------------------------------------
@app.post(
    "/predict",
    response_model=AssetFailurePredictionResponse,
    summary="Asset Failure Prediction & RUL",
    tags=["Predictive Maintenance"],
)
@app.post(
    "/api/v1/predict/asset-failure",
    response_model=AssetFailurePredictionResponse,
    tags=["Predictive Maintenance"],
)
async def predict(payload: AssetTelemetryInput) -> AssetFailurePredictionResponse:
    """Predict asset failure probability, remaining useful life, and risk level."""
    telemetry_dict = payload.model_dump()
    result = predict_asset_failure(
        asset_id=payload.asset_id,
        telemetry_features=telemetry_dict,
        asset_type=payload.asset_type,
    )
    return AssetFailurePredictionResponse(**result)


@app.post(
    "/forecast-demand",
    response_model=DemandForecastResponse,
    summary="Spare-Part Demand Forecasting",
    tags=["Demand Forecasting"],
)
@app.post(
    "/api/v1/forecast/demand",
    response_model=DemandForecastResponse,
    tags=["Demand Forecasting"],
)
async def get_demand_forecast(payload: DemandForecastInput) -> DemandForecastResponse:
    """Compute statistical spare-part demand forecast, safety stock, ROP, and stockout risk."""
    historical_demand = payload.historical_daily_demand

    if not historical_demand:
        data_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "spare_parts_demand.csv"
        if data_path.exists():
            try:
                df = pd.read_csv(data_path)
                subset = df[df["part_id"] == payload.part_id]
                if not subset.empty:
                    historical_demand = subset["daily_demand"].tolist()
            except Exception:
                pass

    if not historical_demand:
        historical_demand = [1.2, 1.0, 1.5, 0.8, 1.3, 1.1, 0.9, 1.4, 1.6, 1.0]

    result = forecast_spare_part_demand(
        part_id=payload.part_id,
        historical_daily_demand=historical_demand,
        forecast_days=payload.forecast_days,
        current_stock=payload.current_stock,
        lead_time_days=payload.lead_time_days,
    )
    return DemandForecastResponse(**result)


@app.post(
    "/operations-decision",
    response_model=UnifiedOperationsDecisionResponse,
    summary="Unified Asset & Inventory Decision",
    tags=["Unified Operations"],
)
@app.post(
    "/api/v1/operations-decision",
    response_model=UnifiedOperationsDecisionResponse,
    tags=["Unified Operations"],
)
async def get_operations_decision(payload: UnifiedOperationsDecisionInput) -> UnifiedOperationsDecisionResponse:
    """Combines asset failure prediction with spare-part demand forecasting and inventory optimization."""
    telemetry = {
        "vibration_mm_s": payload.vibration_mm_s,
        "operating_temp_c": payload.operating_temp_c,
        "ambient_temp_c": payload.ambient_temp_c,
        "power_kw": payload.power_kw,
        "runtime_hours": payload.runtime_hours,
        "last_maintenance_days": payload.last_maintenance_days,
    }

    historical_demand = payload.historical_daily_demand
    if not historical_demand:
        data_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "spare_parts_demand.csv"
        if data_path.exists():
            try:
                df = pd.read_csv(data_path)
                subset = df[df["part_id"] == payload.required_spare_part]
                if not subset.empty:
                    historical_demand = subset["daily_demand"].tolist()
            except Exception:
                pass

    decision = evaluate_unified_operations_decision(
        asset_id=payload.asset_id,
        telemetry_features=telemetry,
        asset_type=payload.asset_type,
        asset_criticality=payload.asset_criticality,
        required_spare_part=payload.required_spare_part,
        current_stock=payload.current_stock,
        lead_time_days=payload.lead_time_days,
        historical_daily_demand=historical_demand,
        forecast_days=payload.forecast_days,
    )
    return UnifiedOperationsDecisionResponse(**decision)


@app.post(
    "/dispatch-technician",
    response_model=TechnicianDispatchResponse,
    summary="Technician Suitability & Route Optimization",
    tags=["Technician Dispatch"],
)
@app.post(
    "/api/v1/dispatch/technician",
    response_model=TechnicianDispatchResponse,
    tags=["Technician Dispatch"],
)
async def dispatch_technician(payload: TechnicianDispatchInput) -> TechnicianDispatchResponse:
    """Scores technician suitability, calculates travel distance & ETA in Dubai corridors, and checks SLA risk."""
    candidates = payload.candidates
    if not candidates:
        candidates = [{
            "technician_id": payload.technician_id or "TECH-DXB-042",
            "skills": payload.technician_skills,
            "availability": payload.technician_availability,
            "current_location": payload.technician_current_location,
            "technician_workload": payload.technician_workload,
        }]

    decision = select_best_technician(
        candidates=candidates,
        required_skill=payload.required_skill or "HVAC_CHILLER_SPECIALIST",
        asset_location=payload.asset_location,
        sla_deadline_hours=payload.sla_deadline_hours,
        estimated_repair_duration_hours=payload.estimated_repair_duration_hours,
    )
    return TechnicianDispatchResponse(**decision)


@app.post(
    "/optimize-operation",
    response_model=OptimizeOperationResponse,
    summary="Cost & SLA Optimization",
    tags=["Cost & SLA Optimization"],
)
@app.post(
    "/api/v1/optimize/operation",
    response_model=OptimizeOperationResponse,
    tags=["Cost & SLA Optimization"],
)
async def optimize_operation(payload: OptimizeOperationInput) -> OptimizeOperationResponse:
    """Cost-benefit tradeoff between preventive intervention and breakdown downtime/SLA penalties."""
    result = optimize_operational_decision(
        failure_probability=payload.failure_probability,
        asset_criticality=payload.asset_criticality,
        maintenance_priority=payload.maintenance_priority,
        stock_status=payload.stock_status,
        selected_technician=payload.selected_technician,
        technician_eta_minutes=payload.technician_eta_minutes,
        sla_status=payload.sla_status,
        spare_part_cost=payload.spare_part_cost,
        current_stock=payload.current_stock,
        reorder_point=payload.reorder_point,
    )
    return OptimizeOperationResponse(**result)


@app.post(
    "/recommend",
    response_model=DecisionIntelligenceResponse,
    summary="Decision Intelligence Rule Synthesis",
    tags=["Decision Intelligence"],
)
@app.post(
    "/decision-intelligence",
    response_model=DecisionIntelligenceResponse,
    tags=["Decision Intelligence"],
)
async def get_decision_intelligence(payload: DecisionIntelligenceInput) -> DecisionIntelligenceResponse:
    """Synthesize asset failure risk and spare-part availability into deterministic recommendations."""
    decision = evaluate_decision_intelligence(
        failure_probability=payload.failure_probability,
        risk_level=payload.asset_risk_level,
        asset_criticality=payload.asset_criticality,
        required_spare_part=payload.required_spare_part,
        current_stock=payload.current_stock,
        minimum_stock=payload.minimum_stock,
        lead_time_days=payload.lead_time_days,
    )
    return DecisionIntelligenceResponse(**decision)
