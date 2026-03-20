from time import perf_counter

from adapter.config.model import AppConfig
from adapter.http.fastapi.dependencies import get_container
from fastapi import FastAPI, Request, Response

REQUEST_COUNT = 'http.server.request.count'
REQUEST_DURATION = 'http.server.request.duration'


def register_middleware(app: FastAPI, config: AppConfig) -> None:
    @app.middleware('http')
    async def request_logging_middleware(
        request: Request,
        call_next,
    ) -> Response:
        start = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (perf_counter() - start) * 1000
            container = get_container(request)
            container.observability.logger.info(
                'http_request',
                attrs={
                    'http.method': request.method,
                    'http.path': request.url.path,
                    'http.status_code': status_code,
                    'http.duration_ms': duration_ms,
                },
            )

    if not config.metrics.enabled:
        return

    @app.middleware('http')
    async def metrics_middleware(
        request: Request,
        call_next,
    ) -> Response:
        start = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (perf_counter() - start) * 1000
            container = get_container(request)
            route = request.scope.get('route')
            path = getattr(route, 'path', None)
            attrs: dict[str, str | int] = {
                'http.method': request.method,
                'http.path': path if isinstance(path, str) and path else 'unmatched',
                'http.status_code': status_code,
            }
            container.observability.metrics.increment(REQUEST_COUNT, attrs=attrs)
            container.observability.metrics.record(
                REQUEST_DURATION,
                duration_ms,
                attrs=attrs,
            )
