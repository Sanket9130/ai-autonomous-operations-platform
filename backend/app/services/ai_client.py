"""
AI Engine HTTP Client.
Handles communication, timeouts, error parsing, and graceful fallbacks for backend requests to the AI Engine.
"""

from typing import Any, Dict
from fastapi import HTTPException, status
import httpx
from backend.app.config import settings


class AIEngineClient:
    """HTTP Client for communicating with the AI Autonomous Operations Engine."""

    def __init__(self, base_url: str = settings.AI_ENGINE_URL, timeout: float = settings.AI_ENGINE_TIMEOUT_SECONDS):
        self.endpoint_url = base_url
        self.timeout = timeout

    async def call_autonomous_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute POST request to AI Engine's /autonomous-operation endpoint.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.endpoint_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return response.json()

            except httpx.ConnectError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Unable to connect to AI Engine at {self.endpoint_url}. Ensure the AI microservice is running. ({str(exc)})",
                )
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"AI Engine request timed out after {self.timeout}s at {self.endpoint_url}.",
                )
            except httpx.HTTPStatusError as exc:
                try:
                    error_detail = exc.response.json().get("detail", exc.response.text)
                except Exception:
                    error_detail = exc.response.text

                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"AI Engine returned error: {error_detail}",
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error communicating with AI Engine: {str(exc)}",
                )


ai_client = AIEngineClient()
