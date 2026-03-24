from time import perf_counter

from fastapi import FastAPI, Request, Response

from adapter.config.model import AppConfig
from adapter.http.fastapi.dependencies import get_container


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
            attrs: dict[str, str | int | float | bool] = {
                'http.method': request.method,
                'http.path': request.url.path,
                'http.status_code': status_code,
                'http.duration_ms': duration_ms,
            }
            container.observability.logger.info(
                'http_request',
                attrs=attrs,
            )
