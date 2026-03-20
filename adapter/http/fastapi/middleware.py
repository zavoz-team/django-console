from time import perf_counter

from adapter.http.fastapi.dependencies import get_container
from fastapi import FastAPI, Request, Response

REQUEST_COUNT = 'http.server.request.count'
REQUEST_DURATION = 'http.server.request.duration'


def register_middleware(app: FastAPI) -> None:
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
            attrs: dict[str, str | int] = {
                'http.method': request.method,
                'http.path': _metric_path(request),
                'http.status_code': status_code,
            }
            container.observability.metrics.increment(REQUEST_COUNT, attrs=attrs)
            container.observability.metrics.record(
                REQUEST_DURATION,
                duration_ms,
                attrs=attrs,
            )


def _metric_path(request: Request) -> str:
    route = request.scope.get('route')
    path = getattr(route, 'path', None)
    if isinstance(path, str) and path:
        return path
    return 'unmatched'
