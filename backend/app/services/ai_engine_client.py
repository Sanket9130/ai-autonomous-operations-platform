import logging
import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError
from backend.app.core.config import settings
from backend.app.schemas.ai_engine import AIEngineResponse, AIEngineRequest

logger = logging.getLogger(__name__)


class AIEngineClient:
    def __init__(self, base_url: str = None, timeout_seconds: float = None):
        self.base_url = (base_url or settings.AI_ENGINE_URL).rstrip("/")
        self.timeout = timeout_seconds or settings.AI_ENGINE_TIMEOUT_SECONDS

    async def call_autonomous_operation(self, request: AIEngineRequest) -> AIEngineResponse:
        """
        Sends telemetry, maintenance, and inventory data to the AI Engine for autonomous decision.
        Strictly handles:
          - Connection failures (502 Bad Gateway)
          - Timeouts (504 Gateway Timeout)
          - HTTP 4xx / 5xx errors (502 Bad Gateway with upstream details)
          - Malformed JSON / Invalid Schema (502 Bad Gateway)
        Never returns fake or fabricated results if the upstream service fails.
        """
        target_url = f"{self.base_url}/autonomous-operation"
        payload = request.model_dump()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(target_url, json=payload)
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
