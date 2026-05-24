"""
Unit tests for OTel trace context injection in CoreApiClient._request().

Covers:
  1. inject() populates carrier and traceparent reaches the outgoing request headers.
  2. Headers forwarded on every retry attempt (not just the first).
  3. Existing timeout / network-error behaviour is preserved.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from types import TracebackType
from typing import Any
from unittest.mock import MagicMock, call, patch

import httpx
import pytest

from adapter.config.model import CoreApiConfig
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNetworkError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def _make_config(
    *,
    retry_attempts: int | None = 0,
    retry_backoff_ms: int | None = 0,
) -> CoreApiConfig:
    return CoreApiConfig(
        base_url="http://core-api",
        timeout_seconds=5,
        service_token_header="X-Service-Token",
        service_token="secret",
        retry_attempts=retry_attempts,
        retry_backoff_ms=retry_backoff_ms,
    )


class _FakeSpan:
    """Minimal Span that records calls for assertion."""

    def __init__(self) -> None:
        self.attributes: dict[str, Any] = {}
        self.errors: list[Exception] = []

    def set_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value

    def record_error(self, error: Exception) -> None:
        self.errors.append(error)


class _FakeSpanContext:
    def __init__(self, span: _FakeSpan) -> None:
        self._span = span

    def __enter__(self) -> _FakeSpan:
        return self._span

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return None


class _FakeTracer:
    def start_span(self, name: str, attrs: Any = None) -> _FakeSpanContext:
        return _FakeSpanContext(_FakeSpan())


def _ok_response(payload: dict[str, Any] | None = None) -> MagicMock:
    """Return a mock httpx.Response that raises nothing and returns JSON."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.content = b"ok"
    resp.json.return_value = payload or {"ok": True}
    resp.raise_for_status.return_value = None
    return resp


def _build_client(
    config: CoreApiConfig | None = None,
) -> tuple[CoreApiClient, MagicMock]:
    """
    Build a CoreApiClient with a mocked httpx.Client.
    Returns (client_instance, mock_httpx_client).
    """
    cfg = config or _make_config()
    tracer = _FakeTracer()
    client = CoreApiClient(cfg, tracer)  # type: ignore[arg-type]

    mock_httpx = MagicMock(spec=httpx.Client)
    mock_httpx.base_url = httpx.URL("http://core-api/")
    mock_httpx.headers = httpx.Headers(
        {cfg.service_token_header: cfg.service_token}
    )
    client._client = mock_httpx  # inject mock
    return client, mock_httpx


# ---------------------------------------------------------------------------
# 1. inject() populates carrier and traceparent reaches outgoing headers
# ---------------------------------------------------------------------------


def test_inject_called_once_per_request():
    """inject() must be called exactly once inside _request()."""
    client, mock_httpx = _build_client()
    mock_httpx.request.return_value = _ok_response()

    with patch("repository.core_api.client.inject") as mock_inject:
        mock_inject.side_effect = lambda carrier: carrier.update(
            {"traceparent": FAKE_TRACEPARENT}
        )
        client._request("GET", "/api/v1/health")

    mock_inject.assert_called_once()


def test_traceparent_header_present_in_outgoing_request():
    """When inject sets a traceparent, that header must appear in the httpx call."""
    client, mock_httpx = _build_client()
    mock_httpx.request.return_value = _ok_response()

    with patch("repository.core_api.client.inject") as mock_inject:
        mock_inject.side_effect = lambda carrier: carrier.update(
            {"traceparent": FAKE_TRACEPARENT}
        )
        client._request("GET", "/api/v1/health")

    _args, kwargs = mock_httpx.request.call_args
    sent_headers = dict(kwargs["headers"])
    assert sent_headers.get("traceparent") == FAKE_TRACEPARENT


def test_no_traceparent_header_when_inject_is_noop():
    """When inject does not write any keys, no traceparent header must be sent."""
    client, mock_httpx = _build_client()
    mock_httpx.request.return_value = _ok_response()

    with patch("repository.core_api.client.inject"):  # default: no side effect
        client._request("GET", "/api/v1/health")

    _args, kwargs = mock_httpx.request.call_args
    sent_headers = dict(kwargs["headers"])
    assert "traceparent" not in sent_headers


def test_extra_headers_and_traceparent_both_forwarded():
    """extra_headers and OTel traceparent must both appear in outgoing headers."""
    client, mock_httpx = _build_client()
    mock_httpx.request.return_value = _ok_response()

    with patch("repository.core_api.client.inject") as mock_inject:
        mock_inject.side_effect = lambda carrier: carrier.update(
            {"traceparent": FAKE_TRACEPARENT}
        )
        client._request(
            "GET",
            "/api/v1/health",
            extra_headers={"X-Custom": "my-value"},
        )

    _args, kwargs = mock_httpx.request.call_args
    sent_headers = dict(kwargs["headers"])
    # httpx.Headers normalises names to lower-case
    assert sent_headers.get("traceparent") == FAKE_TRACEPARENT
    assert sent_headers.get("x-custom") == "my-value"


# ---------------------------------------------------------------------------
# 2. Headers forwarded on every retry attempt
# ---------------------------------------------------------------------------


def test_traceparent_forwarded_on_every_retry():
    """All retry attempts must include the traceparent header, not just the first."""
    cfg = _make_config(retry_attempts=2, retry_backoff_ms=0)
    client, mock_httpx = _build_client(config=cfg)

    # First two calls time out, third succeeds.
    mock_httpx.request.side_effect = [
        httpx.TimeoutException("timeout"),
        httpx.TimeoutException("timeout"),
        _ok_response(),
    ]

    with patch("repository.core_api.client.inject") as mock_inject, patch(
        "repository.core_api.client.time.sleep"
    ):
        mock_inject.side_effect = lambda carrier: carrier.update(
            {"traceparent": FAKE_TRACEPARENT}
        )
        client._request("GET", "/api/v1/health")

    assert mock_httpx.request.call_count == 3
    for call_args in mock_httpx.request.call_args_list:
        _, kwargs = call_args
        sent_headers = dict(kwargs["headers"])
        assert sent_headers.get("traceparent") == FAKE_TRACEPARENT, (
            "traceparent must be present on every attempt"
        )


def test_inject_called_once_even_with_retries():
    """inject() should be called once per _request() invocation, not per attempt."""
    cfg = _make_config(retry_attempts=1, retry_backoff_ms=0)
    client, mock_httpx = _build_client(config=cfg)

    mock_httpx.request.side_effect = [
        httpx.NetworkError("down"),
        _ok_response(),
    ]

    with patch("repository.core_api.client.inject") as mock_inject, patch(
        "repository.core_api.client.time.sleep"
    ):
        mock_inject.side_effect = lambda carrier: None
        client._request("GET", "/api/v1/health")

    mock_inject.assert_called_once()


# ---------------------------------------------------------------------------
# 3. Existing timeout / network-error behaviour is preserved
# ---------------------------------------------------------------------------


def test_raises_network_error_after_retries_exhausted_on_timeout():
    """CoreApiNetworkError must be raised when all timeout retries are exhausted."""
    cfg = _make_config(retry_attempts=1, retry_backoff_ms=0)
    client, mock_httpx = _build_client(config=cfg)

    mock_httpx.request.side_effect = httpx.TimeoutException("timeout")

    with patch("repository.core_api.client.inject"), patch(
        "repository.core_api.client.time.sleep"
    ):
        with pytest.raises(CoreApiNetworkError, match="timed out"):
            client._request("GET", "/api/v1/health")


def test_raises_network_error_after_retries_exhausted_on_network_error():
    """CoreApiNetworkError must be raised when all network-error retries are exhausted."""
    cfg = _make_config(retry_attempts=1, retry_backoff_ms=0)
    client, mock_httpx = _build_client(config=cfg)

    mock_httpx.request.side_effect = httpx.NetworkError("connection refused")

    with patch("repository.core_api.client.inject"), patch(
        "repository.core_api.client.time.sleep"
    ):
        with pytest.raises(CoreApiNetworkError, match="Network error"):
            client._request("GET", "/api/v1/health")


def test_no_retry_when_retry_attempts_is_zero():
    """With retry_attempts=0 the request must fail immediately on first timeout."""
    cfg = _make_config(retry_attempts=0, retry_backoff_ms=0)
    client, mock_httpx = _build_client(config=cfg)

    mock_httpx.request.side_effect = httpx.TimeoutException("timeout")

    with patch("repository.core_api.client.inject"), patch(
        "repository.core_api.client.time.sleep"
    ) as mock_sleep:
        with pytest.raises(CoreApiNetworkError):
            client._request("GET", "/api/v1/health")

    mock_httpx.request.assert_called_once()
    mock_sleep.assert_not_called()


def test_success_on_first_attempt_no_retries_needed():
    """A successful first response must be returned without any retry."""
    client, mock_httpx = _build_client()
    mock_httpx.request.return_value = _ok_response({"data": 42})

    with patch("repository.core_api.client.inject"):
        result = client._request("GET", "/api/v1/health")

    assert result == {"data": 42}
    mock_httpx.request.assert_called_once()
