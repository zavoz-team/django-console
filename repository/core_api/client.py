import json
import time
from typing import Any

import httpx

from adapter.config.model import CoreApiConfig
from repository.core_api.errors import (
    CoreApiDataError,
    CoreApiError,
    CoreApiHttpError,
    CoreApiNetworkError,
    CoreApiNotFoundError,
    CoreApiUnauthorizedError,
)


class CoreApiClient:
    def __init__(self, config: CoreApiConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout_seconds,
            headers={config.service_token_header: config.service_token},
        )

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        attempts = 0
        while True:
            attempts += 1
            try:
                response = self._client.request(method, path, **kwargs)
                response.raise_for_status()
                if not response.content:
                    return {}
                return response.json()
            except httpx.TimeoutException as exc:
                if attempts > (self._config.retry_attempts or 0):
                    raise CoreApiNetworkError("Request timed out") from exc
                time.sleep((self._config.retry_backoff_ms or 0) / 1000)
            except httpx.NetworkError as exc:
                if attempts > (self._config.retry_attempts or 0):
                    raise CoreApiNetworkError("Network error") from exc
                time.sleep((self._config.retry_backoff_ms or 0) / 1000)
            except httpx.HTTPStatusError as exc:
                detail = None
                try:
                    error_json = exc.response.json()
                    detail = error_json.get("detail", str(exc))
                except json.JSONDecodeError:
                    detail = exc.response.text

                if exc.response.status_code == 404:
                    raise CoreApiNotFoundError(detail=detail) from exc
                if exc.response.status_code in (401, 403):
                    raise CoreApiUnauthorizedError(
                        status_code=exc.response.status_code, detail=detail
                    ) from exc
                raise CoreApiHttpError(
                    status_code=exc.response.status_code, detail=detail
                ) from exc
            except json.JSONDecodeError as exc:
                raise CoreApiDataError("Invalid JSON response") from exc
            except Exception as exc:
                raise CoreApiError(f"An unexpected error occurred: {exc}") from exc

    def get_profiles(self, limit: int, offset: int) -> dict[str, Any]:
        return self._request("GET", "/api/v1/profiles", params={"limit": limit, "offset": offset})

    def get_profile(self, customer_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/profiles/{customer_id}")

    def get_segments(self, limit: int, offset: int) -> dict[str, Any]:
        return self._request("GET", "/api/v1/segments", params={"limit": limit, "offset": offset})

    def get_segment_members(self, segment_id: str, limit: int, offset: int) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/segments/{segment_id}/members", params={"limit": limit, "offset": offset})

    def trigger_export(self, segment_id: str) -> dict[str, Any]:
        return self._request("POST", "/api/v1/exports", json={"segment_id": segment_id})

    def get_jobs(self, limit: int, offset: int) -> dict[str, Any]:
        return self._request("GET", "/api/v1/jobs", params={"limit": limit, "offset": offset})

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/jobs/{job_id}")

    def get_system_status(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/health")

    def log_audit_action(self, payload: dict[str, Any]) -> None:
        self._request("POST", "/api/v1/audit/log", json=payload)
