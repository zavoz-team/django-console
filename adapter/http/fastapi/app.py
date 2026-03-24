from collections.abc import Callable

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from adapter.config.loader import load_config
from adapter.config.model import AppConfig
from adapter.di.container import AppContainer, build_container
from adapter.http.fastapi.dependencies import APP_CONFIG_STATE, APP_CONTAINER_STATE
from adapter.http.fastapi.middleware import register_middleware
from adapter.http.fastapi.routers.v1.router import router as v1_router

API_V1_PREFIX = '/api/v1'


def create_app(config: AppConfig | None = None) -> FastAPI:
    app_config = load_config() if config is None else config
    container = build_container(config=app_config)
    app: FastAPI | None = None

    try:
        app = FastAPI(title=app_config.app.name)
        setattr(app.state, APP_CONFIG_STATE, app_config)
        setattr(app.state, APP_CONTAINER_STATE, container)
        app.add_event_handler('shutdown', _build_shutdown_handler(app, container))
        register_middleware(app, app_config)
        app.include_router(v1_router, prefix=API_V1_PREFIX)

        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=container.observability.tracer_provider,
            meter_provider=container.observability.meter_provider,
            exclude_spans=['send', 'receive'],
        )

        return app
    except Exception:
        try:
            if app is not None:
                _uninstrument_app(app)
        finally:
            container.shutdown()
        raise


def _build_shutdown_handler(
    app: FastAPI,
    container: AppContainer,
) -> Callable[[], None]:
    def shutdown() -> None:
        try:
            _uninstrument_app(app)
        finally:
            container.shutdown()

    return shutdown


def _uninstrument_app(app: FastAPI) -> None:
    if _is_instrumented(app):
        FastAPIInstrumentor.uninstrument_app(app)


def _is_instrumented(app: FastAPI) -> bool:
    return bool(getattr(app, '_is_instrumented_by_opentelemetry', False))
