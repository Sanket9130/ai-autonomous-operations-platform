import logging
from typing import Union, Dict, Any
import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError
from backend.app.core.config import settings
from backend.app.schemas.ai_engine import AIEngineResponse, AIEngineRequest

logger = logging.getLogger(__name__)


class AIEngineClient:
    def __init__(self, base_url: str = None, timeout_seconds: float = None):
        raw_url = base_url or settings.AI_ENGINE_URL
        # Ensure base_url does not end with /autonomous-operation if configured as full path
        if "/autonomous-operation" in raw_url:
            self.base_url = raw_url.replace("/autonomous-operation", "").rstrip("/")
        else:
            self.base_url = raw_url.rstrip("/")
        self.timeout = timeout_seconds or settings.AI_ENGINE_TIMEOUT_SECONDS

    async def call_autonomous_operation(self, request: Union[AIEngineRequest, Dict[str, Any]]) -> AIEngineResponse:
        """
        Sends telemetry, maintenance, and inventory data to the AI Engine for autonomous decision.
        Strictly handles:
          - Connection failures (502 Bad Gateway)
          - Timeouts (504 Gateway Timeout)
          - Preserves existing HTTPExceptions
          - Upstream HTTP errors (502 Bad Gateway)
          - Malformed JSON / Schema mismatch (502 Bad Gateway)
        Never returns fake or fabricated results if the upstream service fails.
        """
        # If request is already an AIEngineResponse (e.g. from mock), return directly
        if isinstance(request, AIEngineResponse):
            return request

        target_url = f"{self.base_url}/autonomous-operation"

        if isinstance(request, dict):
            payload = request
        elif hasattr(request, "model_dump"):
            # If AIEngineRequest, adapt fields to AutonomousOperationInput format
            req_dict = request.model_dump()
            telem = req_dict.get("telemetry", {})
            spare_parts = req_dict.get("spare_parts", [])
            first_part = spare_parts[0] if spare_parts else {}

            payload = {
                "asset_id": req_dict.get("asset_id", "UNKNOWN"),
                "asset_type": req_dict.get("asset_type", "HVAC_CHILLER"),
                "asset_location": "MARINA",
                "vibration_mm_s": float(telem.get("vibration_rms", 1.0)),
                "operating_temp_c": float(telem.get("bearing_temperature", 65.0)),
                "ambient_temp_c": 42.0,
                "power_kw": float(telem.get("power_kw", 30.0)),
                "runtime_hours": float(telem.get("operating_hours", 5000.0)),
                "last_maintenance_days": int(req_dict.get("maintenance_history", {}).get("past_failures_count", 0)),
                "asset_criticality": "CRITICAL",
                "required_spare_part": first_part.get("part_id", "PART-BRG-7701"),
                "current_stock": float(first_part.get("current_stock", 0.0)),
                "lead_time_days": float(first_part.get("lead_time", 7.0)),
                "forecast_days": 30,
                "spare_part_cost": float(first_part.get("unit_cost", 450.0)),
                "sla_deadline_hours": 3.0,
                "estimated_repair_duration_hours": 1.5,
            }
        else:
            payload = dict(request)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(target_url, json=payload)
        except HTTPException:
            # Preserve already raised HTTPExceptions
            raise
        except (httpx.ConnectError, httpx.NetworkError) as exc:
            logger.error(f"Failed to connect to AI Engine at {target_url}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Engine unavailable at {self.base_url}. Connection refused or network unreachable."
            )
        except (httpx.TimeoutException, httpx.ReadTimeout, httpx.WriteTimeout) as exc:
            logger.error(f"Timeout communicating with AI Engine at {target_url} ({self.timeout}s): {exc}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"AI Engine request timed out after {self.timeout} seconds."
            )
        except Exception as exc:
            logger.error(f"Unexpected error communicating with AI Engine: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with AI Engine: {str(exc)}"
            )

        # Check HTTP status from AI Engine
        if response.status_code >= 400:
            logger.error(f"AI Engine responded with HTTP {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Engine returned error HTTP {response.status_code}: {response.text[:200]}"
            )

        # Parse and validate JSON response
        try:
            raw_data = response.json()
        except Exception as exc:
            logger.error(f"AI Engine returned invalid JSON: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI Engine returned invalid JSON payload."
            )

        try:
            validated_response = AIEngineResponse.model_validate(raw_data)
            return validated_response
        except ValidationError as exc:
            logger.error(f"AI Engine response schema validation failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Engine returned response that does not match expected schema: {exc.errors()[:2]}"
            )


ai_engine_client = AIEngineClient()
