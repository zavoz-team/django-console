import json
import time
from typing import Any, Optional

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
from usecase.interface import Tracer


class CoreApiClient:
    def __init__(self, config: CoreApiConfig, tracer: Tracer) -> None:
        self._config = config
        self._tracer = tracer
        default_headers = {config.service_token_header: config.service_token}
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout_seconds,
            headers=default_headers,
        )

    def shutdown(self) -> None:
        self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        span_name = f"core_api.{method.lower()}"
        full_url = f"{self._client.base_url}{path}"

        with self._tracer.start_span(
            span_name,
            attrs={
                "http.method": method,
                "http.url": full_url,
                "server.address": str(self._client.base_url),
            },
        ) as span:
            attempts = 0
            request_headers = self._client.headers.copy()
            if extra_headers:
                request_headers.update(extra_headers)

            while True:
                attempts += 1
                try:
                    response = self._client.request(
                        method, path, headers=request_headers, **kwargs
                    )
                    span.set_attribute("http.status_code", response.status_code)
                    response.raise_for_status()
                    if not response.content:
                        return {}
                    return response.json()
                except httpx.TimeoutException as exc:
                    span.record_error(exc)
                    if attempts > (self._config.retry_attempts or 0):
                        raise CoreApiNetworkError("Request timed out") from exc
                    time.sleep((self._config.retry_backoff_ms or 0) / 1000)
                except httpx.NetworkError as exc:
                    span.record_error(exc)
                    if attempts > (self._config.retry_attempts or 0):
                        raise CoreApiNetworkError("Network error") from exc
                    time.sleep((self._config.retry_backoff_ms or 0) / 1000)
                except httpx.HTTPStatusError as exc:
                    span.record_error(exc)
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
                    span.record_error(exc)
                    raise CoreApiDataError("Invalid JSON response") from exc
                except Exception as exc:
                    span.record_error(exc)
                    raise CoreApiError(f"An unexpected error occurred: {exc}") from exc

    def get_profiles(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/profiles",
            params={"limit": limit, "offset": offset},
            extra_headers=extra_headers,
        )

    def get_profile(
        self, customer_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "GET", f"/api/v1/profiles/{customer_id}", extra_headers=extra_headers
        )

    def get_segments(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/segments",
            params={"limit": limit, "offset": offset},
            extra_headers=extra_headers,
        )

    def get_segment_members(
        self,
        segment_id: str,
        limit: int,
        offset: int,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/api/v1/segments/{segment_id}/members",
            params={"limit": limit, "offset": offset},
            extra_headers=extra_headers,
        )

    def trigger_export(
        self, segment_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/exports",
            json={"segment_id": segment_id},
            extra_headers=extra_headers,
        )

    def get_jobs(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/jobs",
            params={"limit": limit, "offset": offset},
            extra_headers=extra_headers,
        )

    def get_job(
        self, job_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request(
            "GET", f"/api/v1/jobs/{job_id}", extra_headers=extra_headers
        )

    def get_system_status(
        self, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return self._request("GET", "/api/v1/health", extra_headers=extra_headers)

    def log_audit_action(
        self, payload: dict[str, Any], extra_headers: Optional[dict[str, str]] = None
    ) -> None:
        self._request("POST", "/api/v1/audit/log", json=payload, extra_headers=extra_headers)
